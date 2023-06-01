# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoDM
                                 A QGIS plugin
 This plugin provides geophysical data management tasks inside metadata database by stepanosokin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-30
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Stepan Osokin
        email                : stepanosokin@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QTableWidgetItem, QTableWidget, QPushButton
from qgis.core import Qgis, QgsProject, QgsLayerTreeUtils, QgsVectorLayerSelectedFeatureSource, QgsMapLayer, QgsMapLayerType
import os, sys, psycopg2, subprocess


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .geo_dm_dialogs import *
import os.path


class GeoDM:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoDM_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Geophysical Data Management')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        with open('.pgdsn', encoding='utf-8') as dsnf:
            dsn = dsnf.read().replace('\n', '')
        self.pgconn = psycopg2.connect(dsn)

        self.proc_list = []

        self.processings = 'dm.processings'
        self.processings_view = 'dm.processings_view'
        self.processing_types = 'dm.processing_types'
        self.projects = 'dm.projects'
        self.companies = 'dm.companies'
        self.contracts = 'dm.contracts'
        self.contracts_view = 'dm.contracts_view'
        self.reports = 'dm.reports'
        self.reports_view = 'dm.reports_view'
        self.projects = 'dm.projects'

        self.seismic_lines_processed_2d = 'dm.seismic_lines_processed_2d'
        self.seismic_pols_processed_3d = 'dm.seismic_pols_processed_3d'

        self.selectedProcLayer = None

        self.selectedProcFeaturesList = []

        self.sql = ''

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeoDM', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/geo_dm/icon.png'
        self.add_action(
            ':/plugins/geo_dm/procseis.png',
            text=self.tr(u'Manage Processed Seismic'),
            callback=self.run_mps,
            parent=self.iface.mainWindow())

        self.add_action(
            ':/plugins/geo_dm/fieldseis.png',
            text=self.tr(u'Manage Field Seismic'),
            callback=self.run_mfs,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Geophysical Data Management'),
                action)
            self.iface.removeToolBarIcon(action)


    def get_proc_from_postgres(self):
        try:
            # with open('.pgdsn', encoding='utf-8') as dsnf:
            # dsn = dsnf.read().replace('\n', '')
            # mpgconn = psycopg2.connect(dsn)
            with self.pgconn.cursor() as cur:
                # cur = pgconn.cursor()
                cur.execute(f"select * from {self.processings_view} order by name")
                # processings = cur.fetchall()
                self.proc_list = list(cur.fetchall())
                # cur.close()
                # dsnf.close()
                return (True)

        except:
            print('error requesting processings list from postgres')
            return (False)
        pass


    def refresh_processings(self):
        self.dockwind.procTableWidget.clear()
        self.dockwind.procTableWidget.setRowCount(0)
        self.dockwind.procTableWidget.setColumnCount(3)
        self.dockwind.procTableWidget.setHorizontalHeaderLabels(['Название', 'Автор', 'Год'])
        # processings = self.get_proc_from_postgres()
        if self.get_proc_from_postgres():
        # if processings[0]:
        #     for i, proc_row in enumerate(processings[1]):
            for i, proc_row in enumerate(self.proc_list):
                self.dockwind.procTableWidget.insertRow(i)
                citem = QTableWidgetItem(proc_row[2])
                citem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.dockwind.procTableWidget.setItem(i, 0, citem)
                citem = QTableWidgetItem(proc_row[9])
                citem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.dockwind.procTableWidget.setItem(i, 1, citem)
                citem = QTableWidgetItem(str(proc_row[6]))
                citem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.dockwind.procTableWidget.setItem(i, 2, citem)


    def execute_sql(self):
        try:
            with self.pgconn.cursor() as cur:
                cur.execute(self.sql)
                self.pgconn.commit()
                [self.iface.messageBar().popWidget(x) for x in self.iface.messageBar().items()]
                self.iface.messageBar().pushMessage('Запрос выполнен', self.sql,
                                                    level=Qgis.Success, duration=3)
                # [self.iface.messageBar().popWidget(x) for x in self.iface.messageBar().items()]
        except:
            self.iface.messageBar().pushMessage('Запрос не выполнен', self.sql,
                                                level=Qgis.Critical, duration=5)


    def update_proc_for_selected_features(self):
        selected_cells = self.dockwind.procTableWidget.selectedItems()
        selected_rows = list(set([x.row() for x in selected_cells]))
        if len(selected_rows) != 1:
            self.iface.messageBar().pushMessage('Ошибка', 'Нужно выбрать один проект по обработке', level=Qgis.Warning, duration=3)
        else:
            proc_id = self.proc_list[selected_rows[0]][1]
            # self.iface.messageBar().pushMessage('Информация', f"Выбрана обработка {str(proc_id)}", level=Qgis.Success, duration=5)
            if self.selectedProcLayer != None and len(self.selectedProcFeaturesList) > 0:
                if 'line_id' in [f.name() for f in self.selectedProcLayer.fields()]:
                    # self.iface.messageBar().pushMessage('Информация', f"Выбран слой с сейсмикой 2D",
                    #                                     level=Qgis.Success, duration=5)
                    if len(self.selectedProcFeaturesList) > 0:
                        line_id_list = [x['line_id'] for x in self.selectedProcFeaturesList]
                        sql = f"update {self.seismic_lines_processed_2d} set proc_id = {str(proc_id)} where line_id in ({', '.join([str(y) for y in line_id_list])});"
                        self.sql = sql

                        # self.iface.messageBar().pushMessage('Запрос', sql,
                        #                                     level=Qgis.Success, duration=5)
                        mwidget = self.iface.messageBar().createMessage(f"Изменить обработку для {len(line_id_list)} объектов?")
                        mbutton = QPushButton(mwidget)
                        mbutton.setText('Подтвердить')
                        mbutton.pressed.connect(self.execute_sql)
                        mwidget.layout().addWidget(mbutton)
                        self.iface.messageBar().pushWidget(mwidget, Qgis.Warning, duration=3)

                elif 'pol_id' in [f.name() for f in self.selectedProcLayer.fields()]:
                    # self.iface.messageBar().pushMessage('Информация', f"Выбран слой с сейсмикой 3D",
                    #                                     level=Qgis.Success, duration=5)
                    pass
            else:
                self.iface.messageBar().pushMessage('Ошибка', f"Нужно выбрать слой и объекты в нем", level=Qgis.Warning, duration=5)





    def display_selected_geometry_count(self):
        self.dockwind.selectedGeometryLabel.setText(f"Выбрано {len(self.selectedProcFeaturesList)} объектов")


    def set_selected_proc_features_list(self):
        ltreenode = QgsProject.instance().layerTreeRoot().children()
        layers = list(filter(lambda x: x.type() == QgsMapLayerType.VectorLayer and x.isSpatial(),
                             QgsLayerTreeUtils().collectMapLayersRecursive(ltreenode)))
        selectedLayerIndex = self.dockwind.layersComboBox.currentIndex()
        # selectedLayer = layers[selectedLayerIndex]
        self.selectedProcLayer = layers[selectedLayerIndex]
        # self.selectedProcFeaturesList = selectedLayer.selectedFeatures()
        self.selectedProcFeaturesList = self.selectedProcLayer.selectedFeatures()


    def add_project(self):
        self.addprojdlg = AddProjDialog()
        new_proj_name_ru = self.addprojdlg.projNameRuInput.text()
        new_proj_name_en = self.addprojdlg.projNameEnInput.text()

        def generate_sql():
            new_proj_name_ru = self.addprojdlg.projNameRuInput.text()
            new_proj_name_en = self.addprojdlg.projNameEnInput.text()
            if new_proj_name_ru and new_proj_name_en:
                fields_to_update = 'name_ru, name_en'
                values_to_insert = f"'{new_proj_name_ru}', '{new_proj_name_en}'"
                self.sql = f"insert into {self.projects}({fields_to_update}) values({values_to_insert})"
                self.iface.messageBar().pushMessage('sql:', self.sql, level=Qgis.Success, duration=5)

        def insert_new_proj():
            new_proj_name_ru = self.addprojdlg.projNameRuInput.text()
            new_proj_name_en = self.addprojdlg.projNameEnInput.text()
            if new_proj_name_ru and new_proj_name_en:
                mwidget = self.iface.messageBar().createMessage(f"Добавить в базу новый проект {new_proj_name_ru}?")
                mbutton = QPushButton(mwidget)
                mbutton.setText('Подтвердить')
                mbutton.pressed.connect(self.execute_sql)
                mwidget.layout().addWidget(mbutton)
                self.iface.messageBar().pushWidget(mwidget, Qgis.Warning, duration=3)
                self.addprojdlg.accept()
            else:
                self.iface.messageBar().pushMessage('Ошибка', 'Укажите название нового проекта на всех языках', level=Qgis.Warning,
                                                    duration=3)

        generate_sql()
        self.addprojdlg.projNameRuInput.editingFinished.connect(generate_sql)
        self.addprojdlg.projNameEnInput.editingFinished.connect(generate_sql)

        self.addprojdlg.insertProjButton.clicked.connect(insert_new_proj)

        self.addprojdlg.show()


    def add_proc(self):
        self.addprocdlg = AddProcDialog()
        self.addprocdlg.refreshProjButton.setIcon(QIcon(':/plugins/geo_dm/refresh.png'))
        self.addprocdlg.refreshAuthorsButton.setIcon(QIcon(':/plugins/geo_dm/refresh.png'))
        self.addprocdlg.refreshContractsButton.setIcon(QIcon(':/plugins/geo_dm/refresh.png'))
        self.addprocdlg.refreshReportsButton.setIcon(QIcon(':/plugins/geo_dm/refresh.png'))

        try:
            def reload_proc_data():
                self.addprocdlg.procTypeInput.clear()
                self.addprocdlg.projectInput.clear()
                self.addprocdlg.procAuthorInput.clear()
                self.addprocdlg.procContractInput.clear()
                self.addprocdlg.procReportInput.clear()
                with self.pgconn.cursor() as cur:
                    sql = f"select * from {self.processing_types} order by id"
                    cur.execute(sql)
                    self.addprocdlg.proc_types = list(cur.fetchall())
                    self.addprocdlg.procTypeInput.addItems([row[2] for row in self.addprocdlg.proc_types])
                    sql = f"select * from {self.projects}"
                    cur.execute(sql)
                    self.addprocdlg.projects = list(cur.fetchall())
                    self.addprocdlg.projectInput.addItems([row[1] for row in self.addprocdlg.projects])
                    sql = f"select * from {self.companies} order by name"
                    cur.execute(sql)
                    self.addprocdlg.companies = list(cur.fetchall())
                    self.addprocdlg.procAuthorInput.addItem('')
                    self.addprocdlg.procAuthorInput.addItems([row[1] for row in self.addprocdlg.companies])
                    sql = f"select * from {self.contracts_view} order by date DESC"
                    cur.execute(sql)
                    self.addprocdlg.contracts = cur.fetchall()
                    self.addprocdlg.procContractInput.addItem('')
                    self.addprocdlg.procContractInput.addItems([row[2] + ' от ' + str(row[3]) + ' ' + row[7] + '-' + row[10] for row in self.addprocdlg.contracts])
                    sql = f"select * from {self.reports_view} order by shortname DESC"
                    cur.execute(sql)
                    self.addprocdlg.reports = cur.fetchall()
                    self.addprocdlg.procReportInput.addItem('')
                    self.addprocdlg.procReportInput.addItems([row[3] for row in self.addprocdlg.reports])

            reload_proc_data()

            def generate_sql():
                new_proc_name = self.addprocdlg.procNameInput.text()
                new_proc_year = str(self.addprocdlg.procYearInput.value())
                selected_proc_type_index = self.addprocdlg.procTypeInput.currentIndex()
                selected_proc_type_id = self.addprocdlg.proc_types[selected_proc_type_index][1]
                selected_project_index = self.addprocdlg.projectInput.currentIndex()
                selected_project_id = self.addprocdlg.projects[selected_project_index][0]
                selected_author_index = self.addprocdlg.procAuthorInput.currentIndex() - 1
                selected_contract_index = self.addprocdlg.procContractInput.currentIndex() - 1
                selected_report_index = self.addprocdlg.procReportInput.currentIndex() - 1
                fields_to_update = 'name, proc_type_id, year, project_id'
                values_to_insert = f"'{new_proc_name}', {str(selected_proc_type_id)}, {str(new_proc_year)}, {str(selected_project_id)}"
                if selected_author_index >= 0:
                    fields_to_update += ', author_id'
                    selected_author_id = self.addprocdlg.companies[selected_author_index][0]
                    values_to_insert += f", {str(selected_author_id)}"
                if selected_contract_index >= 0:
                    fields_to_update += ', contract_id'
                    selected_contract_id = self.addprocdlg.contracts[selected_contract_index][1]
                    values_to_insert += f", {str(selected_contract_id)}"
                if selected_report_index >= 0:
                    fields_to_update += ', report_id'
                    selected_report_id = self.addprocdlg.reports[selected_report_index][1]
                    values_to_insert += f", {str(selected_report_id)}"
                self.sql = f"insert into {self.processings}({fields_to_update}) values({values_to_insert})"
                # self.iface.messageBar().pushMessage('sql:', self.sql, level=Qgis.Success, duration=5)


            def insert_new_proc():
                new_proc_name = self.addprocdlg.procNameInput.text()
                if new_proc_name.strip() != '':
                    mwidget = self.iface.messageBar().createMessage(f"Добавить в базу новую обработку {new_proc_name}?")
                    mbutton = QPushButton(mwidget)
                    mbutton.setText('Подтвердить')
                    mbutton.pressed.connect(self.execute_sql)
                    mwidget.layout().addWidget(mbutton)
                    self.iface.messageBar().pushWidget(mwidget, Qgis.Warning, duration=3)
                    self.addprocdlg.accept()
                else:
                    self.iface.messageBar().pushMessage('Ошибка', 'Укажите название новой обработки', level=Qgis.Warning, duration=3)

            generate_sql()
            self.addprocdlg.procNameInput.editingFinished.connect(generate_sql)
            self.addprocdlg.procTypeInput.activated.connect(generate_sql)
            self.addprocdlg.projectInput.activated.connect(generate_sql)
            self.addprocdlg.procYearInput.valueChanged.connect(generate_sql)
            self.addprocdlg.procYearInput.textChanged.connect(generate_sql)
            self.addprocdlg.procAuthorInput.activated.connect(generate_sql)
            self.addprocdlg.procContractInput.activated.connect(generate_sql)
            self.addprocdlg.procReportInput.activated.connect(generate_sql)
            self.addprocdlg.addProjectButton.clicked.connect(self.add_project)
            self.addprocdlg.refreshProjButton.clicked.connect(reload_proc_data)
            self.addprocdlg.refreshAuthorsButton.clicked.connect(reload_proc_data)
            self.addprocdlg.refreshContractsButton.clicked.connect(reload_proc_data)
            self.addprocdlg.refreshReportsButton.clicked.connect(reload_proc_data)

            # self.addprocdlg.insertProcButton.clicked.connect(self.addprocdlg.done())
            self.addprocdlg.insertProcButton.clicked.connect(insert_new_proc)

        except:
            self.iface.messageBar().pushMessage('Ошибка', 'Не удалось загрузить данные', level=Qgis.Warning, duration=3)

        self.addprocdlg.show()


    def run_mps(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            # self.dlg = GeoDMDialogProc()
            self.dockwind = GeoDMDockWidgetProc()
        else:
            # self.dlg = GeoDMDialogProc()
            self.dockwind = GeoDMDockWidgetProc()

        ltreenode = QgsProject.instance().layerTreeRoot().children()
        layers = list(filter(lambda x: x.type() == QgsMapLayerType.VectorLayer and x.isSpatial(), QgsLayerTreeUtils().collectMapLayersRecursive(ltreenode)))

        self.dockwind.layersComboBox.clear()
        self.dockwind.layersComboBox.addItems([layer.name() for layer in layers])
        self.dockwind.layersComboBox.activated.connect(self.set_selected_proc_features_list)
        self.dockwind.layersComboBox.activated.connect(self.display_selected_geometry_count)
        self.iface.mapCanvas().selectionChanged.connect(self.set_selected_proc_features_list)
        self.iface.mapCanvas().selectionChanged.connect(self.display_selected_geometry_count)

        self.refresh_processings()
        self.dockwind.refreshProcButton.clicked.connect(self.refresh_processings)
        self.dockwind.addProcPushButton.clicked.connect(self.add_proc)
        self.dockwind.changeProcPushButton.clicked.connect(self.update_proc_for_selected_features)

        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwind)
        self.dockwind.adjustSize()
        selectedLayerIndex = self.dockwind.layersComboBox.currentIndex()

        selectedLayer = layers[selectedLayerIndex]



    def run_mfs(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dockwind = GeoDMDialogField()
        else:
            self.dockwind = GeoDMDialogField()

        # show the dialog
        self.dockwind.show()
        # Run the dialog event loop
        result = self.dockwind.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
