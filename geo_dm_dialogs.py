# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoDMDialog
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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
# from PyQt5.QtWebEngineWidgets import QWebEngineView


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_dialog_base.ui'))

class GeoDMDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GeoDMDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


FORM_CLASS_PROC, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_dialog_seis_proc.ui'))

class GeoDMDialogProc(QtWidgets.QDialog, FORM_CLASS_PROC):
    def __init__(self, parent=None):
        """Constructor."""
        super(GeoDMDialogProc, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_FIELD, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_dialog_seis_field.ui'))

class GeoDMDialogField(QtWidgets.QDialog, FORM_CLASS_FIELD):
    def __init__(self, parent=None):
        """Constructor."""
        super(GeoDMDialogField, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_DOCK_PROC, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_dockwidget_seis_proc.ui'))

class GeoDMDockWidgetProc(QtWidgets.QDockWidget, FORM_CLASS_DOCK_PROC):
    def __init__(self, parent=None):
        """Constructor."""
        super(GeoDMDockWidgetProc, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_PROC, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_proc_dialog.ui'))

class AddProcDialog(QtWidgets.QDialog, FORM_CLASS_ADD_PROC):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddProcDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_PROJ, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_proj_dialog.ui'))

class AddProjDialog(QtWidgets.QDialog, FORM_CLASS_ADD_PROJ):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddProjDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_COMP, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_comp_dialog.ui'))

class AddCompDialog(QtWidgets.QDialog, FORM_CLASS_ADD_COMP):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddCompDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_CONTRACT, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_contract_dialog.ui'))

class AddContractDialog(QtWidgets.QDialog, FORM_CLASS_ADD_CONTRACT):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddContractDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_REPORT, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_report_dialog.ui'))

class AddReportDialog(QtWidgets.QDialog, FORM_CLASS_ADD_REPORT):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddReportDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_SURVEY, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_survey_dialog.ui'))

class AddSurveyDialog(QtWidgets.QDialog, FORM_CLASS_ADD_SURVEY):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddSurveyDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_DATASET, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_dataset_dialog.ui'))

class AddDatasetDialog(QtWidgets.QDialog, FORM_CLASS_ADD_DATASET):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddDatasetDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_DRIVE, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_drive_dialog.ui'))

class AddDriveDialog(QtWidgets.QDialog, FORM_CLASS_ADD_DRIVE):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddDriveDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_LINK, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_link_dialog.ui'))

class AddLinkDialog(QtWidgets.QDialog, FORM_CLASS_ADD_LINK):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddLinkDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_ADD_TRANSMITTAL, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_dm_add_transmittal_dialog.ui'))

class AddTransmittalDialog(QtWidgets.QDialog, FORM_CLASS_ADD_TRANSMITTAL):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddTransmittalDialog, self).__init__(parent)
        self.setupUi(self)