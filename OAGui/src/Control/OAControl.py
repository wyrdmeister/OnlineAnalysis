# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Control - Main program

Version 1.0

Michele Devetta (c) 2013


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import re

# PyQt
from PyQt4 import QtCore
from PyQt4 import QtGui

# PyTango
import PyTango as PT

# GuiBase
from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAControl")

# Attribute model
from OAAttrModel import AttributeModel
from OAAttrModel import PushButtonDelegate

# Ui
from Ui import Ui_OAControl


class MainWindow(QtGui.QMainWindow, Ui_OAControl, GuiBase):

    """ OAControl main window. """

    def __init__(self, parent=None):
        # Parent constructors
        QtGui.QMainWindow.__init__(self, parent)
        GuiBase.__init__(self, "OAControl")

        # Setup UI
        self.setupUi(self)

        # Init dialog list
        self.dialogs = []

        # Attribute model
        self.attr_model = None

        # OA device
        self.oadev = None

        # Start timer
        self.startTimer(1000)

        # Center windows
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())

        # Disable buttons
        self.clear_button.setDisabled(True)
        self.plot_selection.setDisabled(True)
        self.save_selection.setDisabled(True)
        self.saveall_button.setDisabled(True)
        self.reload_oa_button.setDisabled(True)

        # Error model
        model = QtGui.QStandardItemModel()
        self.error_log.setModel(model)

    @QtCore.pyqtSlot()
    def timerEvent(self, event):
        """ Timer event handler. Check status of OA servers and update the
        attribute model. """
        try:
            status = self.attr_model.dev.State()
            if status == PT.DevState.ON:
                self.tango_status.setText("ON")
                self.tango_status.setStyleSheet("background-color: green; color: white")
        except:
            self.tango_status.setText("UNKNOWN")
            self.tango_status.setStyleSheet("background-color: red; color: white")

        if isinstance(self.attr_model, AttributeModel) and isinstance(self.attr_model.dev, PT.DeviceProxy):
            try:
                # Enable buttons if needed
                self.clear_button.setDisabled(False)
                self.plot_selection.setDisabled(False)
                self.save_selection.setDisabled(False)
                self.saveall_button.setDisabled(False)

                # Refresh attribute model
                self.attr_model.refresh.emit()

                # Refresh dialogs
                for d in self.dialogs:
                    (val, err) = self.attr_model.fetch_values(d.names)
                    if len(err) == 0 and len(val) > 0:
                        d.refresh_signal.emit(val)
            except Exception, e:
                self.logger.error("Exception while refreshing (Error: %s)", e)

        else:
            # Disable buttons
            self.clear_button.setDisabled(True)
            self.plot_selection.setDisabled(True)
            self.save_selection.setDisabled(True)
            self.saveall_button.setDisabled(True)

        # Update OA server stuff
        if self.oadev is not None:
            self.reload_oa_button.setDisabled(False)
            try:
                status = self.oadev.ProcessingState()
                if status == PT.DevState.RUNNING:
                    self.oa_status.setText("RUNNING")
                    self.oa_status.setStyleSheet("background-color: green; color: white")
                elif status == PT.DevState.STANDBY:
                    self.oa_status.setText("IDLE")
                    self.oa_status.setStyleSheet("background-color: yellow; color: black")
                elif status == PT.DevState.OFF:
                    self.oa_status.setText("OFF")
                    self.oa_status.setStyleSheet("background-color: yellow; color: black")
                else:
                    raise
            except:
                self.oa_status.setText("UNKNOWN")
                self.oa_status.setStyleSheet("background-color: red; color: white")

            try:
                status = self.oadev.ErrorState()
                if status == PT.DevState.ALARM:
                    self.oa_error.setText("WARN")
                    self.oa_error.setStyleSheet("background-color: orange; color: white")
                elif status == PT.DevState.FAULT:
                    self.oa_error.setText("FAULT")
                    self.oa_error.setStyleSheet("background-color: red; color: white")
                elif status == PT.DevState.ON:
                    self.oa_error.setText("ON")
                    self.oa_error.setStyleSheet("background-color: green; color: white")
                    self.error_log.model().clear()
                else:
                    raise
            except:
                self.oa_error.setText("UNKNOWN")
                self.oa_error.setStyleSheet("background-color: red; color: white")

            try:
                err = self.oadev.getErrors(20)
                model = self.error_log.model()
                if len(err) > 0:
                    for e in err:
                        for i in range(model.rowCount()):
                            if e == str(model.item(i).text()):
                                break
                        else:
                            model.appendRow(QtGui.QStandardItem(e))

            except PT.DevFailed, e:
                self.error_log.model().appendRow(QtGui.QStandardItem("Error while fetching errors from WS."))
                for err in e:
                    self.error_log.model().appendRow(QtGui.QStandardItem("TANGO: %s" % err.desc))

            try:
                # Update queue length
                self.oa_queue.setText("%d" % self.oadev.QueueSize)
            except:
                self.oa_queue.setText("n.d.")
        else:
            self.reload_oa_button.setDisabled(True)

    @QtCore.pyqtSlot()
    def on_connect_button_released(self):
        """ Connect to DynAttr server. """
        # Get device
        devname = str(self.tango_device.text())

        # Create AttributeModel
        self.attr_model = AttributeModel(devname, self)

        # Create Proxy model
        self.sort_model = QtGui.QSortFilterProxyModel(self)
        self.sort_model.setSourceModel(self.attr_model)
        self.sort_model.setDynamicSortFilter(True)
        self.sort_model.sort(0)

        # Apply model
        self.tango_list.setModel(self.sort_model)
        # Setup column width
        self.tango_list.resizeColumnsToContents()
        self.tango_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        for i in range(len(self.attr_model.cols_keys) - 3, len(self.attr_model.cols_keys)):
            self.tango_list.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Fixed)
        size = self.tango_list.fontMetrics().size(QtCore.Qt.TextSingleLine, _trUtf8("Reset"))
        self.tango_list.setColumnWidth(5, size.width() + 20)
        size = self.tango_list.fontMetrics().size(QtCore.Qt.TextSingleLine, _trUtf8("Save"))
        self.tango_list.setColumnWidth(6, size.width() + 20)
        size = self.tango_list.fontMetrics().size(QtCore.Qt.TextSingleLine, _trUtf8("View"))
        self.tango_list.setColumnWidth(7, size.width() + 20)
        # Hide order column
        self.tango_list.setColumnHidden(0, True)
        # Setup delegate
        self.tango_list.setItemDelegate(
            PushButtonDelegate(
                [5, 6, 7],
                ["Reset", "Save", "View"],
                [self.attr_model.reset_attribute, self.attr_model.save_attribute, self.attr_model.show_attribute],
                self)
            )

    @QtCore.pyqtSlot()
    def on_connect_oa_button_released(self):
        """ Connect to the WorkSpawner server. """
        try:
            self.oadev = PT.DeviceProxy(str(self.oa_server.text()))

        except PT.DevFailed, e:
            QtGui.QMessageBox.critical(
                        self,
                        _trUtf8("Connection error"),
                        _trUtf8("Connection to OA server failed.\n Error was: %s") % (e[0].desc, ))
            self.oadev = None

    @QtCore.pyqtSlot()
    def on_reload_oa_button_released(self):
        """ Send the reload command to the WorkSpawner server. """
        if self.oadev is not None:
            try:
                self.oadev.command_inout('ReloadConfig')
                QtGui.QMessageBox.information(
                        self,
                        _trUtf8("Configuration reload"),
                        _trUtf8("Configuration was successfully reloaded."))

            except PT.DevFailed, e:
                QtGui.QMessageBox.critical(
                        self,
                        _trUtf8("Command error"),
                        _trUtf8("Configuration reload failed.\n Error was: %s") % (e[0].desc, ))

    @QtCore.pyqtSlot()
    def on_exit_button_released(self):
        """ Close the OAControl GUI. """
        QtGui.qApp.quit()

    @QtCore.pyqtSlot()
    def on_save_selection_released(self):
        """ Save the selected attributes. """
        # Get selected rows
        model = self.tango_list.model()
        rows = list(set([i.row() for i in self.tango_list.selectedIndexes()]))
        names = [str(model.data(model.index(r, 0)).toString()) for r in rows]
        model.sourceModel().save_attrs(names)

    @QtCore.pyqtSlot()
    def on_plot_selection_released(self):
        """ Display the selected attributes. """
        # Get selected rows
        model = self.tango_list.model()
        rows = list(set([i.row() for i in self.tango_list.selectedIndexes()]))
        names = [str(model.data(model.index(r, 0)).toString()) for r in rows]
        if len(names) > 0:
            model.sourceModel().show_attrs(names)

    @QtCore.pyqtSlot()
    def on_saveall_button_released(self):
        """ Save all the attributes. """
        model = self.tango_list.model().sourceModel()
        names = []
        for i in range(model.rowCount()):
            names.append(str(model.index(i, 0).data().toString()))
        self.logger.debug("Saving attributes: %s", names)
        model.save_attrs(names)

    @QtCore.pyqtSlot()
    def on_clear_button_released(self):
        """ Reset all attributes. """
        if self.attr_model is not None:
            ans = QtGui.QMessageBox.question(
                            self,
                            _trUtf8("Attribute clear"),
                            _trUtf8("Are you sure you want to clear all attributes?"),
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                            QtGui.QMessageBox.No)
            if ans == QtGui.QMessageBox.Yes:
                attr_list = self.attr_model.dev.get_attribute_list()
                rexp = re.compile('.*__reset$')
                for a in attr_list:
                    if a == 'State' or a == 'Status':
                        continue
                    if rexp.match(a):
                        self.attr_model.dev.write_attribute(a, True)
                    else:
                        self.attr_model.dev.command_inout('DeleteAttribute', a)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)