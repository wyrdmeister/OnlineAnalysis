# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Editor - Main program

Version 2.0

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

import os
import inspect
import re
from copy import deepcopy
from PyQt4 import QtCore
from PyQt4 import QtGui

from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAEditor")

from OAConfiguration import OAConfiguration
from OAConfiguration import AddDialog
from OAModels import ConfigTableModel
from OAModels import ConfigParameterModel
from OAModels import ComboboxModel
from OADelegate import ColumnDelegate
from OADelegate import CellDelegate
from QLed import QLed

from Ui import Ui_OAEditor


class MainWindow(QtGui.QMainWindow, Ui_OAEditor, GuiBase):

    """ Main windows class
    """

    # Log signal
    log_signal = QtCore.pyqtSignal(unicode)

    def __init__(self, parent=None):
        """ Constructor
        """
        QtGui.QMainWindow.__init__(self, parent)
        GuiBase.__init__(self)

        # Setup UI
        self.setupUi(self)

        # Setup widget logger
        self.logger.setupWidgetLogger(self.log_signal)
        self.log_signal.connect(self.update_log)

        # Center window
        frame = self.frameGeometry()
        frame.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())

        # Init configuration
        self.config = OAConfiguration(self)

        # Update main
        self.update_main()

        # Install eventfilter
        self.online_help_widgets = (QtGui.QLineEdit, QtGui.QPushButton, QtGui.QComboBox, QtGui.QListWidget, QtGui.QTabWidget, QtGui.QTableView)
        for el in dir(self):
            if type(getattr(self, el)) in self.online_help_widgets:
                getattr(self, el).installEventFilter(self)

        # Flag
        self.disableOnDataChanged = False

        # Create LED
        self.statusgood = QLed(True, self.notification)
        self.statusgood.setGeometry(0, 0, 31, 31)

        # Disable TANGO output
        self.en_tango.setCheckState(QtCore.Qt.Unchecked)
        self.on_en_tango_stateChanged(QtCore.Qt.Unchecked)

    ##
    ## Button slots
    ##
    @QtCore.pyqtSlot()
    def on_config_browse_released(self):
        """ Open file browser to select the configuration file. """
        # Call file dialog
        name = unicode(QtGui.QFileDialog.getOpenFileName(
                            self,
                            _trUtf8("Open configuration file"),
                            os.getcwd(),
                            _trUtf8("Configuration file (*.xml)")))
        if name != "":
            # Relative paths works reliably only on posix systems. On windows
            # we just use absolute paths
            if os.name == 'posix':
                # Get path relative to cwd
                relname = os.path.relpath(name, os.getcwd())
                # Count number of relative levels
                count = 0
                for el in relname.split(os.path.sep):
                    if el == os.path.pardir:
                        count += 1
                    else:
                        break
                # If number of levels is less than 3, use relative path
                if count < 3:
                    name = relname
            self.logger.debug("[%s] Selected file '%s'.", inspect.stack()[0][3], name)
            self.config_file.setText(name)

    @QtCore.pyqtSlot()
    def on_config_load_released(self):
        """ Load config button slot. """
        if self.config.load(unicode(self.config_file.text())):
            self.reload_profiles()
        # Update main
        self.update_main()

    @QtCore.pyqtSlot()
    def on_config_save_released(self):
        """ Save config button slot. """
        self.config.save()

    @QtCore.pyqtSlot()
    def on_config_saveas_released(self):
        """ Save as button slot. """
        self.config.saveas()

    @QtCore.pyqtSlot()
    def on_profile_add_released(self):
        """ Add profile button slot. """
        (name, ok) = self.config.addProfile()
        if ok:
            self.reload_profiles(name)

    @QtCore.pyqtSlot()
    def on_profile_delete_released(self):
        """ Delete profile button slot. """
        if self.config.deleteProfile(unicode(self.profile_list.currentText())):
            self.reload_profiles()

    @QtCore.pyqtSlot()
    def on_profile_rename_released(self):
        """ Rename profile slot. """
        (name, ok) = self.config.renameProfile(unicode(self.profile_list.currentText()))
        if ok:
            self.reload_profiles(name)

    @QtCore.pyqtSlot()
    def on_profile_duplicate_released(self):
        """ Duplicate profile slot. """
        (name, ok) = self.config.duplicateProfile(unicode(self.profile_list.currentText()))
        if ok:
            self.reload_profiles(name)

    @QtCore.pyqtSlot()
    def on_output_browse_released(self):
        """ Browse for output file. """
        # Call file dialog
        name = unicode(QtGui.QFileDialog.getSaveFileName(
                                self,
                                _trUtf8("Save OA server configuration file"),
                                os.getcwd(),
                                _trUtf8("Configuration file (*.xml)")))
        if name != "":
            # Relative paths works reliably only on posix systems. On windows
            # we just use absolute paths
            if os.name == 'posix':
                # Get path relative to cwd
                relname = os.path.relpath(name, os.getcwd())
                # Count number of relative levels
                count = 0
                for el in relname.split(os.path.sep):
                    if el == os.path.pardir:
                        count += 1
                    else:
                        break
                # If number of levels is less than 3, use relative path
                if count < 3:
                    name = relname
            # Check that there's a valid extension
            if name[-4:] != '.xml':
                name = name + '.xml'
            self.logger.debug("[%s] Selected file '%s'.", inspect.stack()[0][3], name)
            self.oa_outputfile.addItem(name)
            for i in range(self.oa_outputfile.count()):
                if self.oa_outputfile.itemText(i) == name:
                    self.oa_outputfile.setCurrentIndex(i)
                    break

    @QtCore.pyqtSlot()
    def on_tango_browse_released(self):
        """ Browse TANGO button slot. """
        # First try to import TANGO
        try:
            import PyTango as PT
        except Exception, e:
            QtGui.QMessageBox.critical(
                        self,
                        _trUtf8("Import error"),
                        _trUtf8("Cannot import the PyTango module. The module may be missing or corrupted.\nError was: %s") % (e, ))
            return

        # Connect to database:
        try:
            db = PT.Database()
        except PT.DevFailed, e:
            host = os.environ.get('TANGO_HOST', '').split(':')
            if len(host) == 2:
                msg = _trUtf8("Cannot connect to database server %s on port %d.") % (host[0], host[1])
            else:
                msg = _trUtf8("Cannot connect to database. TANGO_HOST environment variable may be missing or set to a bad value.")
            QtGui.QMessageBox.critical(
                        self,
                        _trUtf8("Import error"),
                        msg)
            return

        # Get list of servers of 'SpawnerWorkerSrv' class
        dev_list = list(db.get_device_exported_for_class("SpawnWorkerSrv").value_string)

        if len(dev_list) > 0:
            (dev, ok) = QtGui.QInputDialog.getItem(
                                    self,
                                    _trUtf8("Select device"),
                                    _trUtf8("Select the WorkSpawner server for the OA:"),
                                    dev_list,
                                    0,
                                    False)
            if ok and dev != "":
                dev_str = "%s:%d/%s" % (db.get_db_host(), db.get_db_port_num(), dev)
                # Search for the device in currently configured values
                for i in range(self.oa_server.count()):
                    if self.oa_server.itemText(i) == dev_str:
                        self.oa_server.setCurrentIndex(i)
                        break
                else:
                    self.oa_server.addItem(dev_str)
                    for i in range(self.oa_server.count()):
                        if self.oa_server.itemText(i) == dev_str:
                            self.oa_server.setCurrentIndex(i)
                            break

        else:
            QtGui.QMessageBox.warning(
                self,
                _trUtf8("No device found."),
                _trUtf8("In the currently selected database there isn't any WorkSpawner device server configured."))

    @QtCore.pyqtSlot()
    def on_output_generate_released(self):
        """ Generate output button slot. """
        if self.config.generate(unicode(self.oa_outputfile.currentText())):
            QtGui.QMessageBox.information(
                        self,
                        _trUtf8(u"Generation successful"),
                        _trUtf8(u"The OA configuration was generated successfully."))

    @QtCore.pyqtSlot()
    def on_output_genreload_released(self):
        """ Generate output and reload button slot. """
        if self.config.generate(unicode(self.oa_outputfile.currentText())):
            self.reload_oa()

    @QtCore.pyqtSlot()
    def on_output_reload_released(self):
        """ Reload button slot. """
        self.reload_oa()

    @QtCore.pyqtSlot()
    def on_fix_errors_released(self):
        """ Fix errors button slot. """
        if len(self.config_errors) > 0:
            self.fix_configuration_errors()

    @QtCore.pyqtSlot()
    def on_raw_add_released(self):
        """ Add new raw dataset button slot. """
        if self.raw_list.model() is None:
            return
        dg = AddDialog('raw dataset', sorted(self.config.rawtypes), self)
        ret = dg.exec_()
        if ret == QtGui.QDialog.Accepted:
            name = unicode(dg.name.text())
            tp = unicode(dg.type.itemText(dg.type.currentIndex()))
            if name != "":
                model = self.raw_list.model().sourceModel()
                for i in range(model.rowCount()):
                    if unicode(model.index(i, 0).data().toString()) == name:
                        # Duplicate name
                        QtGui.QMessageBox.critical(
                                self,
                                _trUtf8(u"Duplicate name"),
                                _trUtf8(u"The chosen name is already in use."))
                        return
                model.addElement(dict(name=name, type=tp, path="", enabled=False))

    @QtCore.pyqtSlot()
    def on_raw_remove_released(self):
        """ Remove raw dataset button slot. """
        # Identify selected rows
        selected_rows = list(set([i.row() for i in self.raw_list.selectedIndexes()]))
        # Check that there's only one
        if len(selected_rows) > 1:
            self.logger.error("[%s] Wrong row selection %s while removing dataset.", inspect.stack()[0][3], selected_rows)
            return
        if len(selected_rows) == 0:
            # No selection
            return

        # Get model
        model = self.raw_list.model()
        # Get source index
        index = model.mapToSource(model.index(selected_rows[0], 0))

        # Ask for confirmation
        ans = QtGui.QMessageBox.question(
                    self,
                    _trUtf8(u"Remove element"),
                    _trUtf8(u"Are you sure to remove dataset '%s'?") % (unicode(index.data().toString()), ),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)
        if ans == QtGui.QMessageBox.Yes:
            # Remove dataset
            self.logger.debug("[%s] Removing dataset '%s'.", inspect.stack()[0][3], unicode(index.data().toString()))
            model.sourceModel().removeElement(index)

    @QtCore.pyqtSlot()
    def on_raw_loadhdf_released(self):
        """ Load HDF button slot. """
        if self.raw_list.model() is not None:
            if self.config.raw_from_h5():
                self.update_raw_model()

    @QtCore.pyqtSlot()
    def on_raw_clear_released(self):
        """ Clear disabled raw datasets button slot. """
        if self.raw_list.model():
            # Ask for confirmation
            ans = QtGui.QMessageBox.question(
                        self,
                        _trUtf8(u"Remove disabled elements"),
                        _trUtf8(u"Are you sure to remove all disabled raw datasets?"),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)
            if ans == QtGui.QMessageBox.Yes:
                model = self.raw_list.model().sourceModel()
                for i in range(model.rowCount() - 1, -1, -1):
                    if not model.index(i, 3).data().toBool():
                        self.logger.debug("[%s] Removing raw dataset '%s'.", inspect.stack()[0][3], str(model.index(i, 0).data().toString()))
                        model.removeElement(i)

    @QtCore.pyqtSlot()
    def on_algo_moveup_released(self):
        """ Slot for button to move an algorithm up in the list. """
        # Get current selection
        selected_rows = list(set([i.row() for i in self.algo_list.selectedIndexes()]))
        if len(selected_rows) > 1:
            self.logger.error("[%s] Wrong row selection %s while moving algorithm.", inspect.stack()[0][3], selected_rows)
            return
        if len(selected_rows) == 0:
            # No selection
            return

        row = selected_rows[0]
        if row > 0:
            # Get index
            model = self.algo_list.model()
            sourcemodel = model.sourceModel()
            curr_index = model.mapToSource(model.index(row, 2))
            up_index = model.mapToSource(model.index(row - 1, 2))
            curr_order = sourcemodel.data(curr_index)
            new_order = sourcemodel.data(up_index)

            # Check that the swap does not hurt, that is the source variables
            # are not from the swapped algo
            in_var = self.config.getAlgoInVars(curr_index.row())
            out_var = self.config.getAlgoOutVars(up_index.row())

            # Actual check
            self.logger.debug("[%s] Input variables: %s - Output variables: %s", inspect.stack()[0][3], in_var, out_var)
            for v in in_var:
                if v in out_var:
                    return

            # Swap orders
            sourcemodel.setData(curr_index, new_order)
            sourcemodel.setData(up_index, curr_order)

    @QtCore.pyqtSlot()
    def on_algo_movedown_released(self):
        """ Slot for button to move an algorithm down in the list. """
        # Get current selection
        selected_rows = list(set([i.row() for i in self.algo_list.selectedIndexes()]))
        if len(selected_rows) > 1:
            self.logger.error("[%s] Wrong row selection %s while moving algorithm.", inspect.stack()[0][3], selected_rows)
            return
        if len(selected_rows) == 0:
            # No selection
            return

        # If it's not the last row, we swap the order with the next one
        row = selected_rows[0]
        if row < self.algo_list.model().rowCount() - 1:
            model = self.algo_list.model()
            sourcemodel = model.sourceModel()
            curr_index = model.mapToSource(model.index(row, 2))
            down_index = model.mapToSource(model.index(row + 1, 2))
            curr_order = sourcemodel.data(curr_index)
            down_order = sourcemodel.data(down_index)

            # Check that the swap does not hurt, that is the source variables
            # are not from the swapped algo
            in_var = self.config.getAlgoInVars(down_index.row())
            out_var = self.config.getAlgoOutVars(curr_index.row())

            # Actual check
            self.logger.debug("[%s] Input variables: %s - Output variables: %s", inspect.stack()[0][3], in_var, out_var)
            for v in in_var:
                if v in out_var:
                    return

            # Swap orders
            sourcemodel.setData(curr_index, down_order)
            sourcemodel.setData(down_index, curr_order)

    @QtCore.pyqtSlot()
    def on_algo_add_released(self):
        """ Slot for add algo button. """
        if self.algo_list.model() is None:
            return
        dg = AddDialog('algorithm', sorted(self.config.algotypes.keys()), self)
        ret = dg.exec_()
        if ret == QtGui.QDialog.Accepted:
            name = unicode(dg.name.text())
            tp = unicode(dg.type.itemText(dg.type.currentIndex()))
            if name != "":
                model = self.algo_list.model().sourceModel()
                o = 0
                for i in range(model.rowCount()):
                    # Check name for duplicate
                    if unicode(model.index(i, 0).data().toString()) == name:
                        # Duplicate name
                        QtGui.QMessageBox.critical(
                                self,
                                _trUtf8(u"Duplicate name"),
                                _trUtf8(u"The chosen name is already in use."))
                        return
                    # Check order
                    if model.index(i, 2).data().toInt()[0] > o:
                        o = model.index(i, 2).data().toInt()[0]
                # Add new element
                model.addElement(dict(name=name, type=tp, order=o + 1, parameters={}, enabled=False))

    @QtCore.pyqtSlot()
    def on_algo_remove_released(self):
        """ Slot for remove algo button. """
        # Identify selected rows
        selected_rows = list(set([i.row() for i in self.algo_list.selectedIndexes()]))
        # Check that there's only one
        if len(selected_rows) > 1:
            self.logger.error("[%s] Wrong row selection %s while removing algorithm.", inspect.stack()[0][3], selected_rows)
            return
        if len(selected_rows) == 0:
            # No selection
            return

        # Get model
        model = self.algo_list.model()
        # Get source index
        index = model.mapToSource(model.index(selected_rows[0], 0))

        # Ask for confirmation
        ans = QtGui.QMessageBox.question(
                    self,
                    _trUtf8(u"Remove element"),
                    _trUtf8(u"Are you sure to remove algorithm '%s'?") % (unicode(index.data().toString()), ),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)
        if ans == QtGui.QMessageBox.Yes:
            # Remove algorithm
            self.logger.debug("[%s] Removing algorithm '%s'.", inspect.stack()[0][3], unicode(index.data().toString()))
            model.sourceModel().removeElement(index)

    @QtCore.pyqtSlot()
    def on_algo_duplicate_released(self):
        """ Duplicate algorithm button slot. """
        r = list(set([i.row() for i in self.algo_list.selectedIndexes()]))
        # Check that there's only one
        if len(r) > 1:
            self.logger.error("[%s] Wrong row selection %s while removing algorithm.", inspect.stack()[0][3], r)
            return
        if len(r) == 0:
            # No selection
            return

        # Map index to source
        r = self.algo_list.model().mapToSource(self.algo_list.model().index(r[0], 0)).row()

        # Ask for a new name
        (name, ok) = QtGui.QInputDialog.getText(
                                self,
                                _trUtf8("Inser name for duplicated algorithm"),
                                _trUtf8("Please insert a name for the duplicated algorithm"),
                                QtGui.QLineEdit.Normal,
                                self.config['algo'][r]['name'])

        name = unicode(name)
        if ok and name != "":
            # Check that the name is unique
            model = self.algo_list.model().sourceModel()
            o = 0
            for i in range(model.rowCount()):
                # Check name for duplicate
                    if unicode(model.index(i, 0).data().toString()) == name:
                        # Duplicate name
                        QtGui.QMessageBox.critical(
                                self,
                                _trUtf8(u"Duplicate name"),
                                _trUtf8(u"The chosen name is already in use."))
                        return
                    # Check order
                    if model.index(i, 2).data().toInt()[0] > o:
                        o = model.index(i, 2).data().toInt()[0]

            # Extract parameters
            params = deepcopy(self.config['algo'][r]['parameters'])
            for p in params:
                if params[p]['type'] == 'outvar':
                    params[p]['value'] = ''

            # Add new element
            model.addElement(dict(name=name, type=self.config['algo'][r]['type'], order=o + 1, parameters=params, enabled=False))

            # Message
            QtGui.QMessageBox.information(
                self,
                _trUtf8("Duplication done"),
                _trUtf8("The selected algorithm have been duplicated. All output parameters have been reset."))

    @QtCore.pyqtSlot()
    def on_algo_clear_released(self):
        """ Clear disabled algorithms button slot. """
        if self.algo_list.model():
            # Ask for confirmation
            ans = QtGui.QMessageBox.question(
                        self,
                        _trUtf8(u"Remove disabled elements"),
                        _trUtf8(u"Are you sure to remove all disabled algorithms?"),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)
            if ans == QtGui.QMessageBox.Yes:
                model = self.algo_list.model().sourceModel()
                for i in range(model.rowCount() - 1, -1, -1):
                    if not model.index(i, 3).data().toBool():
                        self.logger.debug("[%s] Removing algorithm '%s'.", inspect.stack()[0][3], str(model.index(i, 0).data().toString()))
                        model.removeElement(i)

    @QtCore.pyqtSlot()
    def on_pres_add_released(self):
        """ Add presenter button slot. """
        if self.pres_list.model() is None:
            return
        dg = AddDialog('presenter', sorted(self.config.prestypes.keys()), self)
        ret = dg.exec_()
        if ret == QtGui.QDialog.Accepted:
            name = unicode(dg.name.text())
            tp = unicode(dg.type.itemText(dg.type.currentIndex()))
            if name != "":
                model = self.pres_list.model().sourceModel()
                for i in range(model.rowCount()):
                    # Check name for duplicate
                    if unicode(model.index(i, 0).data().toString()) == name:
                        # Duplicate name
                        QtGui.QMessageBox.critical(
                                self,
                                _trUtf8(u"Duplicate name"),
                                _trUtf8(u"The chosen name is already in use."))
                        return
                # Add new element
                model.addElement(dict(name=name, type=tp, parameters={}, filters=[], enabled=False))

    @QtCore.pyqtSlot()
    def on_pres_remove_released(self):
        """ Presenter remove button slot. """
        # Identify selected rows
        selected_rows = list(set([i.row() for i in self.pres_list.selectedIndexes()]))
        # Check that there's only one
        if len(selected_rows) > 1:
            self.logger.error("[%s] Wrong row selection %s while removing presenter.", inspect.stack()[0][3], selected_rows)
            return
        if len(selected_rows) == 0:
            # No selection
            return

        # Get model
        model = self.pres_list.model()
        # Get source index
        index = model.mapToSource(model.index(selected_rows[0], 0))

        # Ask for confirmation
        ans = QtGui.QMessageBox.question(
                    self,
                    _trUtf8(u"Remove element"),
                    _trUtf8(u"Are you sure to remove presenter '%s'?") % (unicode(index.data().toString()), ),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)
        if ans == QtGui.QMessageBox.Yes:
            # Remove presenter
            self.logger.debug("[%s] Removing presenter '%s'.", inspect.stack()[0][3], unicode(index.data().toString()))
            model.sourceModel().removeElement(index)

    @QtCore.pyqtSlot()
    def on_pres_duplicate_released(self):
        """ Duplicate presenter button slot. """
        r = list(set([i.row() for i in self.pres_list.selectedIndexes()]))
        # Check that there's only one
        if len(r) > 1:
            self.logger.error("[%s] Wrong row selection %s while removing algorithm.", inspect.stack()[0][3], r)
            return
        if len(r) == 0:
            # No selection
            return

        # Map index to source
        r = self.pres_list.model().mapToSource(self.pres_list.model().index(r[0], 0)).row()

        # Ask for a new name
        (name, ok) = QtGui.QInputDialog.getText(
                                self,
                                _trUtf8("Inser name for duplicated presenter"),
                                _trUtf8("Please insert a name for the duplicated presenter"),
                                QtGui.QLineEdit.Normal,
                                self.config['pres'][r]['name'])

        name = unicode(name)
        if ok and name != "":
            # Check that the name is unique
            model = self.pres_list.model().sourceModel()
            for i in range(model.rowCount()):
                # Check name for duplicate
                if unicode(model.index(i, 0).data().toString()) == name:
                    # Duplicate name
                    QtGui.QMessageBox.critical(
                            self,
                            _trUtf8(u"Duplicate name"),
                            _trUtf8(u"The chosen name is already in use."))
                    return

            # Extract parameters
            params = deepcopy(self.config['pres'][r]['parameters'])
            for p in params:
                if params[p]['type'] == 'tango':
                    params[p]['value'] = ''

            # Add new element
            model.addElement(dict(name=name, type=self.config['pres'][r]['type'], parameters=params, filters=deepcopy(self.config['pres'][r]['filters']), enabled=False))

            # Message
            QtGui.QMessageBox.information(
                self,
                _trUtf8("Duplication done"),
                _trUtf8("The selected presenter have been duplicated. All output parameters have been reset."))

    @QtCore.pyqtSlot()
    def on_pres_clear_released(self):
        """ Clear disabled presenters button slot. """
        if self.pres_list.model():
            # Ask for confirmation
            ans = QtGui.QMessageBox.question(
                        self,
                        _trUtf8(u"Remove disabled elements"),
                        _trUtf8(u"Are you sure to remove all disabled presenters?"),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)
            if ans == QtGui.QMessageBox.Yes:
                model = self.pres_list.model().sourceModel()
                for i in range(model.rowCount() - 1, -1, -1):
                    if not model.index(i, 2).data().toBool():
                        self.logger.debug("[%s] Removing presenter '%s'.", inspect.stack()[0][3], str(model.index(i, 0).data().toString()))
                        model.removeElement(i)

    @QtCore.pyqtSlot()
    def on_filter_add_released(self):
        """ Filter add button slot. """
        # Get model
        model = self.filter_list.model()
        # Directly add a new element
        if model is not None:
            model.addElement(dict(operator='and', target='', type='eq', value='', enabled=False))

    @QtCore.pyqtSlot()
    def on_filter_remove_released(self):
        """ Remove filter button slot. """
        # Identify selected rows
        selected_rows = list(set([i.row() for i in self.filter_list.selectedIndexes()]))
        # Check that there's only one
        if len(selected_rows) > 1:
            self.logger.error("[%s] Wrong row selection %s while removing filter.", inspect.stack()[0][3], selected_rows)
            return
        if len(selected_rows) == 0:
            # No selection
            return

        # Get model
        model = self.filter_list.model()
        if model is None:
            return
        # Get index
        index = model.index(selected_rows[0], 0)
        # Ask for confirmation
        ans = QtGui.QMessageBox.question(
                    self,
                    _trUtf8(u"Remove element"),
                    _trUtf8(u"Are you sure to remove selected filter?"),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)
        if ans == QtGui.QMessageBox.Yes:
            # Remove filter
            self.logger.debug("[%s] Removing filter %d.", inspect.stack()[0][3], index.row())
            model.removeElement(index)

    @QtCore.pyqtSlot()
    def on_exit_released(self):
        """ Close window """
        self.close()

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        """ Ask confirmation before closing. """
        ans = QtGui.QMessageBox.question(
                        self,
                        _trUtf8("Confirm close"),
                        _trUtf8("Are you sure you want to close? All unsaved changes will be discarded."),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)
        if ans == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    ##
    ## Other slots
    ##
    @QtCore.pyqtSlot(int)
    def on_profile_list_currentIndexChanged(self, index):
        """ Slot to handle profile changes. """
        if index != -1:
            self.config.setCurrentProfile(unicode(self.profile_list.itemText(index)))
            self.update_output_model()
            self.update_raw_model()
            self.update_algo_model()
            self.update_pres_model()
            self.genericOnDataChanged(QtCore.QModelIndex(), QtCore.QModelIndex())
        else:
            self.logger.debug("[%s] Invalid index.", inspect.stack()[0][3])

    @QtCore.pyqtSlot(int)
    def on_en_tango_stateChanged(self, state):
        """ Slot for enable TANGO checkbox. """
        elements = [self.oa_server, self.oa_process, self.oa_postprocess, self.tango_browse, self.output_genreload, self.output_reload]
        if state == QtCore.Qt.Checked:
            for el in elements:
                el.setDisabled(False)
        else:
            for el in elements:
                el.setDisabled(True)

    @QtCore.pyqtSlot(int)
    def on_main_tab_currentChanged(self, index):
        """ On tab change slot. """
        if str(self.main_tab.currentWidget().objectName()) == "output_tab":
            self.logger.debug("[%s] Output tab selected.", inspect.stack()[0][3])
        elif str(self.main_tab.currentWidget().objectName()) == "rawdata_tab":
            self.logger.debug("[%s] Raw data tab selected.", inspect.stack()[0][3])
        elif str(self.main_tab.currentWidget().objectName()) == "algo_tab":
            self.logger.debug("[%s] Algorithms tab selected.", inspect.stack()[0][3])
            # Refresh current selection
            for i in self.algo_list.selectedIndexes():
                self.algo_list.selectionModel().select(i, QtGui.QItemSelectionModel.Clear)
                self.algo_list.selectionModel().select(i, QtGui.QItemSelectionModel.Select)
        elif str(self.main_tab.currentWidget().objectName()) == "pres_tab":
            self.logger.debug("[%s] Presentation tab selected.", inspect.stack()[0][3])
            # Refresh current selection
            for i in self.pres_list.selectedIndexes():
                self.pres_list.selectionModel().select(i, QtGui.QItemSelectionModel.Clear)
                self.pres_list.selectionModel().select(i, QtGui.QItemSelectionModel.Select)
        else:
            self.logger.debug("[%s] No tab selected.", inspect.stack()[0][3])

    ##
    ## Service functions
    ##
    def reload_profiles(self, curr=None):
        """ Reload profiles and reset models. """
        # Keep current profile
        if curr is None:
            curr = unicode(self.profile_list.currentText())
        # Delete all profile names
        self.profile_list.clear()
        # Re-add items to the combobox
        self.profile_list.addItems(self.config.profiles())
        # Search for the previous profile
        if curr in self.config.profiles():
            for i in range(self.profile_list.count()):
                if unicode(self.profile_list.itemText(i)) == curr:
                    self.profile_list.setCurrentIndex(i)
                    break
        else:
            self.profile_list.setCurrentIndex(0)

    def reload_oa(self):
        """ Send the reload config command to the OA TANGO device. """
        # Try to load PyTango
        try:
            import PyTango as PT
        except Exception, e:
            QtGui.QMessageBox.critical(
                    self,
                    _trUtf8(u"Import error"),
                    _trUtf8(u"An error occurred while loading the module PyTango. The module may be missing or have been corrupted.\nError: %s.") % (e, ))
            self.logger.error("[%s] Error importing PyTango (Error: %s)", inspect.stack()[0][3], e)
            return

        # Connect to Tango device
        try:
            dev = PT.DeviceProxy(str(self.oa_server.currentText()))

        except PT.DevFailed, e:
            QtGui.QMessageBox.critical(
                    self,
                    _trUtf8(u"Connection error"),
                    _trUtf8(u"Cannot connect to TANGO device.\nError: %s.") % (e[0].desc, ))

        else:
            try:
                dev.write_attribute('DefaultJobMetaInfo', str(self.oa_process.currentText()))
                dev.write_attribute('DefaultPostMetaInfo', str(self.oa_postprocess.currentText()))
                dev.command_inout('ReloadConfig')

            except PT.DevFailed, e:
                QtGui.QMessageBox.critical(
                        self,
                        _trUtf8(u"Configuration error"),
                        _trUtf8(u"Cannot configure OA TANGO device.\nError was:\n%s") % ("\n".join([err.desc for err in e]), ))

            else:
                QtGui.QMessageBox.information(
                        self,
                        _trUtf8(u"Reset successful"),
                        _trUtf8(u"OA configuration reload was successful."))

    def update_main(self):
        """ Update main configuration controls. """
        elements = [(self.oa_outputfile, 'outfile'),
                    (self.oa_server, 'oa_device'),
                    (self.oa_process, 'oa_process'),
                    (self.oa_postprocess, 'oa_present')]

        # Cycle over elements
        for el in elements:
            # Create elements if non-existent
            if el[1] not in self.config['main']:
                self.config['main'][el[1]] = []

            # Search for currently selected element
            current = None
            for i in range(len(self.config['main'][el[1]])):
                if self.config['main'][el[1]][i][0]:
                    current = i
                    break

            # Configure model
            el[0].setModel(ComboboxModel(self.config['main'][el[1]]))
            # Select curren element
            if current is not None:
                el[0].setCurrentIndex(current)

    @QtCore.pyqtSlot(int)
    def on_oa_outputfile_currentIndexChanged(self, index):
        self.genericMainOnIndexChanged('outfile', index)

    @QtCore.pyqtSlot(int)
    def on_oa_server_currentIndexChanged(self, index):
        self.genericMainOnIndexChanged('oa_device', index)

    @QtCore.pyqtSlot(int)
    def on_oa_process_currentIndexChanged(self, index):
        self.genericMainOnIndexChanged('oa_process', index)

    @QtCore.pyqtSlot(int)
    def on_oa_postprocess_currentIndexChanged(self, index):
        self.genericMainOnIndexChanged('oa_present', index)

    def genericMainOnIndexChanged(self, el, index):
        """ Generic on index change slot for main configuration. """
        if el in self.config['main']:
            for i in range(len(self.config['main'][el])):
                if i == index:
                    self.config['main'][el][i][0] = True
                else:
                    self.config['main'][el][i][0] = False

    def update_output_model(self):
        """ Create a new output model. """
        elements = [(self.oa_module, 'oa', 'module'),
                    (self.oa_class, 'oa', 'class'),
                    (self.oa_path_re, 'oa', 'path_re'),
                    (self.oa_outpath, 'oa', 'outpath'),
                    (self.pres_module, 'present', 'module'),
                    (self.pres_class, 'present', 'class'),
                    (self.pres_device, 'present', 'device')]

        if self.config.currentProfile() is not None:
            for el in elements:
                # Add element if non-existence
                if el[1] not in self.config['output']:
                    self.config['output'][el[1]] = {}
                if el[2] not in self.config['output'][el[1]]:
                    self.config['output'][el[1]][el[2]] = []
                # Search for current
                current = None
                for i in range(len(self.config['output'][el[1]][el[2]])):
                    if self.config['output'][el[1]][el[2]][i][0]:
                        current = i
                        break
                # Configure model
                el[0].setModel(ComboboxModel(self.config['output'][el[1]][el[2]]))
                # Select curren element
                if current is not None:
                    el[0].setCurrentIndex(current)

    @QtCore.pyqtSlot(int)
    def on_oa_module_currentIndexChanged(self, index):
        self.genericOutputOnIndexChanged(('oa', 'module'), index)

    @QtCore.pyqtSlot(int)
    def on_oa_class_currentIndexChanged(self, index):
        self.genericOutputOnIndexChanged(('oa', 'class'), index)

    @QtCore.pyqtSlot(int)
    def on_oa_path_re_currentIndexChanged(self, index):
        self.genericOutputOnIndexChanged(('oa', 'path_re'), index)

    @QtCore.pyqtSlot(int)
    def on_oa_outpath_currentIndexChanged(self, index):
        self.genericOutputOnIndexChanged(('oa', 'outpath'), index)

    @QtCore.pyqtSlot(int)
    def on_pres_module_currentIndexChanged(self, index):
        self.genericOutputOnIndexChanged(('present', 'module'), index)

    @QtCore.pyqtSlot(int)
    def on_pres_class_currentIndexChanged(self, index):
        self.genericOutputOnIndexChanged(('present', 'class'), index)

    @QtCore.pyqtSlot(int)
    def on_pres_device_currentIndexChanged(self, index):
        self.genericOutputOnIndexChanged(('present', 'device'), index)

    def genericOutputOnIndexChanged(self, el, index):
        """ Generic on index change slot. """
        if self.config.currentProfile() is not None:
            if el[0] in self.config['output'] and el[1] in self.config['output'][el[0]]:
                for i in range(len(self.config['output'][el[0]][el[1]])):
                    if i == index:
                        self.config['output'][el[0]][el[1]][i][0] = True
                    else:
                        self.config['output'][el[0]][el[1]][i][0] = False

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def genericOnDataChanged(self, topLeft, bottomRight):
        """ Check integrity of configuration. """
        # If further checks are disabled return
        if self.disableOnDataChanged:
            self.logger.debug("[%s] event ignored.", inspect.stack()[0][3])
            return
        # Chek configuration
        self.config_errors = self.config.verify()
        if len(self.config_errors) > 0:
            # Found errors
            self.logger.warning("[%s] Found %d inconsistencies in configuration.", inspect.stack()[0][3], len(self.config_errors))
            self.statusgood.setValue(False)
        else:
            # No errors found
            self.logger.debug("[%s] No inconsistencies found.", inspect.stack()[0][3])
            self.statusgood.setValue(True)

    def fix_configuration_errors(self):
        """ Check integrity of configuration. """
        # Disable further triggering of the check while we correct errors
        self.disableOnDataChanged = True

        # Cycle over errors and ask what to do
        for miss, srclist in self.config_errors.iteritems():

            self.logger.debug("[%s] '%s' is needed by %s.", inspect.stack()[0][3], miss, srclist)

            exp = re.match(r"([aorv]{1})_(.+)", miss)
            m_type = exp.group(1)
            if m_type == 'v':
                m_src = exp.group(2)
            else:
                m_src = int(exp.group(2))

            # Build dependency list
            deps = []
            for el in srclist:
                if el[0] == 'p':
                    deps.append("presenter '%s'" % (self.config['pres'][el[1]]['name'], ))
                elif el[0] == 'a':
                    deps.append("algorithm '%s'" % (self.config['algo'][el[1]]['name'], ))
                elif el[0] == 'f':
                    deps.append("filter %d of presenter '%s'" % (el[2], self.config['pres'][el[1]]['name']))

            if m_type == 'a':
                # Algo disabled
                name = self.config['algo'][m_src]['name']
                ans = QtGui.QMessageBox.question(
                            self,
                            _trUtf8("Algorithm disabled"),
                            _trUtf8("Algorithms '%s' is needed by %s but it's disabled. Do you want to enable it?\n(If you choose 'No', all dependent elements will be disabled.)") % (name, ", ".join(deps)),
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                            QtGui.QMessageBox.No)

                if ans == QtGui.QMessageBox.Yes:
                    model = self.algo_list.model().sourceModel()
                    index = model.index(m_src, 3)
                    model.setData(index, QtCore.QVariant(True))
                    continue

            elif m_type == 'o':
                # Wrong algo order
                name = self.config['algo'][m_src]['name']
                ans = QtGui.QMessageBox.question(
                            self,
                            _trUtf8("Algorithm disabled"),
                            _trUtf8("Algorithm '%s' is needed by %s but it's set to be excuted later. Do you want to correct the algorithm order?\n(If you choose 'No', all dependent elements will be disabled.)") % (name, ", ".join(deps)),
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                            QtGui.QMessageBox.No)

                if ans == QtGui.QMessageBox.Yes:
                    self.config.resortAlgoOrder()
                    model = self.algo_list.model().sourceModel()
                    model.dataChanged.emit(model.index(0, 2), model.index(model.rowCount() - 1, 2))
                    continue

            elif m_type == 'r':
                # Raw variable disabled
                name = self.config['rawdata'][m_src]['name']
                ans = QtGui.QMessageBox.question(
                            self,
                            _trUtf8("Raw dataset disabled"),
                            _trUtf8("Dataset '%s' is needed by %s but it's disabled. Do you want to enable it?\n(If you choose 'No', all dependent elements will be disabled.)") % (name, ", ".join(deps)),
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                            QtGui.QMessageBox.No)

                if ans == QtGui.QMessageBox.Yes:
                    model = self.raw_list.model().sourceModel()
                    index = model.index(m_src, 3)
                    model.setData(index, QtCore.QVariant(True))
                    continue

            elif m_type == 'v':
                # Variable missing
                QtGui.QMessageBox.warning(
                        self,
                        _trUtf8("Variable missing"),
                        _trUtf8("Variable '%s' is needed by %s but its not defined. All its dependencies will be disabled.") % (m_src, ", ".join(deps)))

            # No action taken, so disable all the dependencies
            for el in srclist:
                if el[0] == 'p':
                    model = self.pres_list.model().sourceModel()
                    index = model.index(el[1], 2)
                    model.setData(index, QtCore.QVariant(False))
                elif el[0] == 'a':
                    model = self.algo_list.model().sourceModel()
                    index = model.index(el[1], 3)
                    model.setData(index, QtCore.QVariant(False))
                elif el[0] == 'f':
                    r = list(set([i.row() for i in self.pres_list.selectedIndexes()]))
                    if len(r) == 1:
                        index = self.pres_list.model().mapToSource(self.pres_list.model().index(r, 0)).row()
                        if index == el[1]:
                            # Edit filter through model
                            model = self.filter_list.model()
                            model.setData(model.index(el[2], 3), False)
                            continue
                    # Edit configuration directly
                    self.config['pres'][el[1]]['filters'][el[2]]['enabled'] = False

        self.disableOnDataChanged = False
        self.genericOnDataChanged(QtCore.QModelIndex(), QtCore.QModelIndex())

    def update_raw_model(self):
        """ Create a new raw dataset model. """
        # Configuration
        raw_delegates = [
            {'column': 1, 'type': 'ComboboxDelegate', 'labels': self.config.rawtypes, 'values': self.config.rawtypes},
            {'column': 3, 'type': 'CheckboxDelegate'}
        ]

        raw_columns = [
            {'name': 'Name', 'id': 'name', 'dtype': unicode, 'unique': True},
            {'name': 'Type', 'id': 'type', 'dtype': unicode, 'unique': False},
            {'name': 'Path', 'id': 'path', 'dtype': unicode, 'unique': False},
            {'name': '', 'id': 'enabled', 'dtype': bool, 'unique': False}
        ]

        # Create model
        model = ConfigTableModel(self.config['rawdata'], raw_columns, self)
        model.dataChanged.connect(self.genericOnDataChanged)
        # Create proxy sorter
        sorter = QtGui.QSortFilterProxyModel(self)
        sorter.setSourceModel(model)
        sorter.setDynamicSortFilter(True)
        sorter.sort(0)
        # Set model in TableView
        self.raw_list.setModel(sorter)
        # Create item delegate
        delegate = ColumnDelegate(raw_delegates, self)
        self.raw_list.setItemDelegate(delegate)
        # Setup column witdh
        self.raw_list.resizeColumnsToContents()
        self.raw_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.raw_list.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.raw_list.horizontalHeader().resizeSection(1, 100)
        self.raw_list.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.raw_list.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.raw_list.horizontalHeader().resizeSection(3, 50)
        # Hide vertical header
        self.raw_list.verticalHeader().hide()
        # Set edit triggers
        self.raw_list.setEditTriggers(QtGui.QTableView.SelectedClicked | QtGui.QTableView.DoubleClicked)
        # Selection mode and behaviour
        self.raw_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.raw_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def update_algo_model(self):
        """ Create a new algorithm model. """
        # Configuration
        algo_delegates = [
            {'column': 1, 'type': 'NullDelegate'},
            {'column': 3, 'type': 'CheckboxDelegate'}
        ]

        algo_columns = [
            {'name': 'Name', 'id': 'name', 'dtype': unicode, 'unique': True},
            {'name': 'Type', 'id': 'type', 'dtype': unicode, 'unique': False},
            {'name': 'Order', 'id': 'order', 'dtype': int, 'unique': False},
            {'name': '', 'id': 'enabled', 'dtype': bool, 'unique': False}
        ]

        # Create model
        model = ConfigTableModel(self.config['algo'], algo_columns, self)
        model.dataChanged.connect(self.genericOnDataChanged)
        # Create proxy sorter
        sorter = QtGui.QSortFilterProxyModel(self)
        sorter.setSourceModel(model)
        sorter.setDynamicSortFilter(True)
        sorter.sort(2)
        # Set model in TableView
        self.algo_list.setModel(sorter)
        # Create item delegate
        delegate = ColumnDelegate(algo_delegates, self)
        self.algo_list.setItemDelegate(delegate)
        # Setup column witdh
        self.algo_list.resizeColumnsToContents()
        self.algo_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.algo_list.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.algo_list.horizontalHeader().resizeSection(3, 50)
        # Hide order column
        self.algo_list.setColumnHidden(2, True)
        # Hide vertical header
        self.algo_list.verticalHeader().hide()
        # Set edit triggers
        self.algo_list.setEditTriggers(QtGui.QTableView.SelectedClicked | QtGui.QTableView.DoubleClicked)
        # Selection mode and behaviour
        self.algo_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.algo_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # Connect onSelectionChanged slot
        self.algo_list.selectionModel().selectionChanged.connect(self.on_algo_list_selectionChanged)

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_algo_list_selectionChanged(self, selected, deselected):
        """ Handle selction of algorithms. """
        r = list(set([i.row() for i in selected.indexes()]))
        if len(r) > 1:
            self.logger.debug("[%s] Got wrong row selection (%s) in algorithm list.", inspect.stack()[0][3], r)
            return
        if len(r) == 0:
            return

        r = r[0]
        # Map index to sourceModel
        model = self.algo_list.model()
        r = model.mapToSource(model.index(r, 0)).row()
        self.logger.debug("[%s] Selected algorithm '%s'.", inspect.stack()[0][3], unicode(model.sourceModel().index(r, 0).data().toString()))

        # Get algorithm type
        atype = self.config.algotypes[self.config['algo'][r]['type']]
        # Create parameter model
        pmodel = ConfigParameterModel(self.config['algo'][r]['parameters'], atype, r, self)
        pmodel.dataChanged.connect(self.genericOnDataChanged)
        # Resort delegates to match order in the parameter list
        delegates = pmodel.resortDelegates(atype, self.config.getAllVars())
        # Set model
        self.algo_param_list.setModel(pmodel)
        # Set item delegates
        self.algo_param_list.setItemDelegate(CellDelegate(delegates))
        # Configure headers
        self.algo_param_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.algo_param_list.horizontalHeader().hide()
        # Set edit triggers
        self.algo_param_list.setEditTriggers(QtGui.QTableView.SelectedClicked | QtGui.QTableView.DoubleClicked)
        # Selection mode and behaviour
        self.algo_param_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.algo_param_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def update_pres_model(self):
        """ Create a new presenter model. """
        # Configuration
        pres_delegates = [
            {'column': 1, 'type': 'NullDelegate'},
            {'column': 2, 'type': 'CheckboxDelegate'}
        ]

        pres_columns = [
            {'name': 'Name', 'id': 'name', 'dtype': unicode, 'unique': True},
            {'name': 'Type', 'id': 'type', 'dtype': unicode, 'unique': False},
            {'name': '', 'id': 'enabled', 'dtype': bool, 'unique': False}
        ]

        # Create model
        model = ConfigTableModel(self.config['pres'], pres_columns, self)
        model.dataChanged.connect(self.genericOnDataChanged)
        # Create proxy sorter
        sorter = QtGui.QSortFilterProxyModel(self)
        sorter.setSourceModel(model)
        sorter.setDynamicSortFilter(True)
        sorter.sort(0)
        # Set model in TableView
        self.pres_list.setModel(sorter)
        # Create item delegate
        self.pres_list.setItemDelegate(ColumnDelegate(pres_delegates, self))
        # Setup column witdh
        self.pres_list.resizeColumnsToContents()
        self.pres_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.pres_list.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)
        self.pres_list.horizontalHeader().resizeSection(2, 50)
        # Hide vertical header
        self.pres_list.verticalHeader().hide()
        # Set edit triggers
        self.pres_list.setEditTriggers(QtGui.QTableView.SelectedClicked | QtGui.QTableView.DoubleClicked)
        # Selection mode and behaviour
        self.pres_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.pres_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # Connect onSelectionChanged slot
        self.pres_list.selectionModel().selectionChanged.connect(self.on_pres_list_selectionChanged)

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_pres_list_selectionChanged(self, selected, deselected):
        """ Handle selction of presenters. """
        r = list(set([i.row() for i in selected.indexes()]))
        if len(r) > 1:
            self.logger.debug("[%s] Got wrong row selection (%s) in presenter list.", inspect.stack()[0][3], r)
            return
        if len(r) == 0:
            return

        r = r[0]
        # Map index to sourceModel
        model = self.pres_list.model()
        r = model.mapToSource(model.index(r, 0)).row()
        self.logger.debug("[%s] Selected presenter '%s'.", inspect.stack()[0][3], unicode(model.sourceModel().index(r, 0).data().toString()))

        # Get presenter type
        ptype = self.config.prestypes[self.config['pres'][r]['type']]
        # Create parameter model
        pmodel = ConfigParameterModel(self.config['pres'][r]['parameters'], ptype, r, self)
        pmodel.dataChanged.connect(self.genericOnDataChanged)
        # Resort delegates to match order in the parameter list
        delegates = pmodel.resortDelegates(ptype, sorted(self.config.getAlgoOutVars()))
        # Set model
        self.pres_param_list.setModel(pmodel)
        # Set item delegates
        self.pres_param_list.setItemDelegate(CellDelegate(delegates))
        # Configure headers
        self.pres_param_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.pres_param_list.horizontalHeader().hide()
        # Set edit triggers
        self.pres_param_list.setEditTriggers(QtGui.QTableView.SelectedClicked | QtGui.QTableView.DoubleClicked)
        # Selection mode and behaviour
        self.pres_param_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.pres_param_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Configure filter model
        filter_delegates = [
            {'column': 0, 'type': 'ComboboxDelegate', 'labels': ['And', 'Or', '!And', '!Or', 'Xor'], 'values': ['and', 'or', 'nand', 'nor', 'xor']},
            {'column': 1, 'type': 'ComboboxDelegate', 'labels': sorted(self.config.getAlgoOutVars()), 'values': sorted(self.config.getAlgoOutVars())},
            {'column': 2, 'type': 'ComboboxDelegate', 'labels': [u"=", u"≠", u"<", u"≤", u">", u"≥", "Expr."], 'values': ['eq', 'neq', 'lt', 'le', 'gt', 'ge', 'expr']},
            {'column': 4, 'type': 'CheckboxDelegate'}
        ]
        filter_columns = [
            {'name': 'Op.', 'id': 'operator', 'dtype': unicode, 'unique': False},
            {'name': 'Target', 'id': 'target', 'dtype': unicode, 'unique': False},
            {'name': 'Type', 'id': 'type', 'dtype': unicode, 'unique': False},
            {'name': 'Value', 'id': 'value', 'dtype': unicode, 'unique': False},
            {'name': '', 'id': 'enabled', 'dtype': bool, 'unique': False}
        ]

        # Set model in TableView
        self.filter_list.setModel(ConfigTableModel(self.config['pres'][r]['filters'], filter_columns, self))
        # Create item delegate
        self.filter_list.setItemDelegate(ColumnDelegate(filter_delegates, self))
        # Setup column witdh
        self.filter_list.resizeColumnsToContents()
        self.filter_list.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.filter_list.horizontalHeader().setResizeMode(4, QtGui.QHeaderView.Fixed)
        self.filter_list.horizontalHeader().resizeSection(4, 40)
        # Hide vertical header
        self.filter_list.verticalHeader().hide()
        # Set edit triggers
        self.filter_list.setEditTriggers(QtGui.QTableView.SelectedClicked | QtGui.QTableView.DoubleClicked)
        # Selection mode and behaviour
        self.filter_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.filter_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def eventFilter(self, obj, event):
        """ Event filter for online help. """
        if type(obj) in self.online_help_widgets:
            if event.type() == QtCore.QEvent.Enter and not obj.whatsThis().isEmpty():
                self.help_text.setText(obj.whatsThis())
            elif event.type() == QtCore.QEvent.Leave:
                self.help_text.setText(_trUtf8("Online help. Move the cursor over a control to see a brief description."))
        return False

    @QtCore.pyqtSlot(unicode)
    def update_log(self, text):
        """ Update log view. """
        self.log_list.addItem(text)
        self.log_list.sortItems(QtCore.Qt.DescendingOrder)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)