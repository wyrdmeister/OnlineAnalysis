# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Control - TANGO attribute model

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
import h5py as h5
import numpy as np

# PyQt4
from PyQt4 import QtCore
from PyQt4 import QtGui

# PyTango
import PyTango as PT

# GuiBase
from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAControl")

# Plot dialog
from OAGui.OAMultiplot import PlotDialog


class AttributeModel(QtCore.QAbstractTableModel, GuiBase):

    """ Attribute model """

    # Signal to refresh attribute list
    refresh = QtCore.pyqtSignal()

    def __init__(self, device, parent=None):
        """ Constructor. """
        # Parent constructor
        QtCore.QAbstractTableModel.__init__(self, parent)
        GuiBase.__init__(self, "OAControl")

        # Store parent
        self._parent = parent

        # Tango device
        try:
            self.dev = PT.DeviceProxy(device)
        except PT.DevFailed, e:
            self.logger.error("Failed to connect to TANGO device (Error: %s)", e[0].desc)
            self.dev = None

        # Connect refresh signal
        self.refresh.connect(self.refresh_model)

        # Attribute list
        self.attributes = []

        self.cols_keys = ['name', 'vartype', 'datatype', 'size', 'acc', 'bstatus', 'bsave', 'bview']

        # Refresh list
        self.refresh.emit()

    @QtCore.pyqtSlot()
    def refresh_model(self):
        """ Refresh the model. """
        if self.dev:
            # Add attributes
            attr_info = self.dev.attribute_list_query()
            attr_list = self.dev.get_attribute_list()
            # Cycle over attributes
            for a in attr_info:
                # Skip state and status
                if a.label == 'State' or a.label == 'Status':
                    continue

                # Skip reset attributes
                rexp = re.compile('.*__reset$')
                if rexp.match(a.label):
                    continue

                # Skip bunches attributes
                rexp = re.compile('.*__bunches$')
                if rexp.match(a.label):
                    continue

                # Skip bunches attributes
                rexp = re.compile('.*__x$')
                if rexp.match(a.label):
                    continue

                # Format size
                size = '1'
                if a.data_format == PT.AttrDataFormat.SPECTRUM:
                    size = "[%d, ]" % (a.max_dim_x, )
                elif a.data_format == PT.AttrDataFormat.IMAGE:
                    size = "[%d, %d]" % (a.max_dim_x, a.max_dim_y)
                elif a.data_format == PT.AttrDataFormat.SCALAR:
                    val = self.dev.read_attribute(a.label).value
                    if val == 0:
                        size = "0"
                    elif val > 0.01 and val < 100:
                        size = "%.4f" % val
                    else:
                        size = "%.4e" % val

                # Accumulated statistic
                acc = -1
                if a.label + "__bunches" in attr_list:
                    acc = len(self.dev.read_attribute(a.label + "__bunches").value)

                # Search attribute
                for at in self.attributes:
                    if at[self.cols_keys[0]] == a.label:
                        # Update entry
                        self.setData(self.index(self.attributes.index(at), 1), QtCore.QVariant(self._tango_atype2str(a.data_format)), QtCore.Qt.EditRole)
                        self.setData(self.index(self.attributes.index(at), 2), QtCore.QVariant(self._tango_dtype2str(a.data_type)), QtCore.Qt.EditRole)
                        self.setData(self.index(self.attributes.index(at), 3), QtCore.QVariant(size), QtCore.Qt.EditRole)
                        self.setData(self.index(self.attributes.index(at), 4), QtCore.QVariant(acc), QtCore.Qt.EditRole)
                        break
                else:
                    # Add attribute
                    self.appendAttribute({
                            self.cols_keys[0]: a.label,
                            self.cols_keys[1]: self._tango_atype2str(a.data_format),
                            self.cols_keys[2]: self._tango_dtype2str(a.data_type),
                            self.cols_keys[3]: size,
                            self.cols_keys[4]: acc,
                            self.cols_keys[5]: False,
                            self.cols_keys[6]: False,
                            self.cols_keys[7]: False})

            # Remove old attributes
            for at in self.attributes:
                for a in attr_list:
                    if a == at[self.cols_keys[0]]:
                        break
                else:
                    self.removeAttribute(self.attributes.index(at))

    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Return row count. """
        return len(self.attributes)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """ Return column count. """
        return len(self.cols_keys)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """ Return data from the model. """
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.attributes[index.row()][self.cols_keys[index.column()]])
        return QtCore.QVariant()

    def setData(self, index, data, role=QtCore.Qt.EditRole):
        """ Modify data in che model. """
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() > 4:
                self.attributes[index.row()][self.cols_keys[index.column()]] = data.toBool()
            else:
                self.attributes[index.row()][self.cols_keys[index.column()]] = str(data.toString())
            self.dataChanged.emit(index, index)
            return True
        return False

    def appendAttribute(self, attribute, parent=QtCore.QModelIndex()):
        """ Append new attribute. """
        self.beginInsertRows(parent, self.rowCount(), self.rowCount())
        self.attributes.append(attribute)
        self.endInsertRows()

    def removeAttribute(self, row, parent=QtCore.QModelIndex()):
        """ Remove attribute. """
        self.beginRemoveRows(parent, row, row)
        del self.attributes[row]
        self.endRemoveRows()

    def clearModel(self, parent=QtCore.QModelIndex()):
        """ Remove all attributes from model. """
        self.beginRemoveRows(parent, 0, self.rowCount() - 1)
        self.attributes = []
        self.endRemoveRows()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ Return headers for the attribute list. """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return QtCore.QVariant("Name")
                elif section == 1:
                    return QtCore.QVariant("Attribute type")
                elif section == 2:
                    return QtCore.QVariant("Data type")
                elif section == 3:
                    return QtCore.QVariant("Size")
                elif section == 4:
                    return QtCore.QVariant("Acc.")
            elif orientation == QtCore.Qt.Vertical:
                return QtCore.QVariant(self.attributes[section]['name'])
        return QtCore.QVariant()

    def reset_attribute(self, index):
        """ Reset a attribute setting the flag in the DynAttr server. """
        if self.dev:
            name = str(self.data(self.index(index.row(), 0)).toString())
            try:
                self.logger.debug("Resetting attribute '%s'", name)
                self.dev.write_attribute(name + "__reset", True)
            except PT.DevFailed, e:
                QtGui.QMessageBox.warning(
                        self._parent,
                        _trUtf8("Cannot reset attribute"),
                        _trUtf8("There was an error while resetting attribute '%s'\nError was: %s") % (name, e.args[0].desc))

    def save_attribute(self, index):
        """ Callback to save one attribute to HDF5. """
        name = str(self.data(self.index(index.row(), 0)).toString())
        self.save_attrs([name, ])

    def save_attrs(self, names):
        """ Callback to save a list of attributes to HDF5. """
        if self.dev:
            # First of all get all the attributes, so that what is saved is
            # what was shown when the save button was pressed
            values = {}
            for name in names:
                try:
                    attr = self.dev.read_attribute(name).value
                    if attr == None:
                        self.logger.warning("Attribute '%s' is empty.", name)
                        continue
                    self.logger.debug("Got attribute '%s': shape = %s.", name, attr.shape)

                    # Try to get bunches
                    try:
                        bunches = self.dev.read_attribute(name + "__bunches").value
                        self.logger.debug("Got bunches for attribute '%s'. Size is %s", name, bunches.shape)

                    except PT.DevFailed, e:
                        bunches = None

                    try:
                        x = self.dev.read_attribute(name + "__x").value
                        self.logger.debug("Got x axis for attribute '%s'. Size is %s", name, x.shape)
                    except PT.DevFailed, e:
                        x = None

                    values[name] = (attr, x, bunches)

                except PT.DevFailed as e:
                    self.logger.error("Failed to get attribute '%s' (Error: %s)", name, e[0].desc)
                    QtGui.QMessageBox.critical(
                            self._parent,
                            _trUtf8("Cannot retrieve attribute"),
                            _trUtf8("Cannot retrieve attribute '%s'\nError was: %s") % (name, e[0].desc))
                    continue

            # Try to open HDF5 file
            try:
                filename = QtGui.QFileDialog.getSaveFileName(
                                self._parent,
                                _trUtf8("Save attribute"),
                                '/home/ldm',
                                _trUtf8("HDF5 files (*.h5 *.hdf5)"))
                if not str(filename):
                    return
                f = h5.File(str(filename), 'w')
            except Exception, e:
                self.logger.error("Failed to save attributes sto file '%s' (Error: %s)", filename, e)
                QtGui.QMessageBox.critical(
                        self._parent,
                        _trUtf8("Error saving file"),
                        _trUtf8("Cannot open file '%s' to save attributes.\nError was: %s") % (filename, e))
                return

            # Save attributes
            for k in values:
                f.create_dataset(k, data=values[k][0])
                if values[k][2] is not None:
                    f.create_dataset(k + "__bunches", data=values[k][2])
                if values[k][1] is not None:
                    f.create_dataset(k + "__x", data=values[k][1])

            # Ask for a comment
            (comment, ok) = QtGui.QInputDialog.getText(
                                                    self._parent,
                                                    _trUtf8("Insert a comment"),
                                                    _trUtf8("Insert a comment in the HDF5 file. Press cancel to skip."))
            if ok:
                self.logger.debug("Inserted comment was: %s", comment)
                f.create_dataset("Comment", data=str(comment))

            # Close file
            f.close()

    def fetch_values(self, names):
        """ Fetch attribute values from TANGO. """
        val = []
        err = []
        for name in names:
            try:
                y = self.dev.read_attribute(name).value
                try:
                    x = self.dev.read_attribute(name + "__x").value
                    val.append((x, y))
                except PT.DevFailed:
                    val.append(y)

            except PT.DevFailed, e:
                self.logger.error("Failed to get attribute '%s' (Error: %s)", name, e[0].desc)
                err.append(e[0].desc)
        return (val, err)

    def show_attribute(self, index):
        """ Callback to show one attribute. """
        if self.dev:
            self.show_attrs([str(self.data(self.index(index.row(), 0)).toString()), ])

    def show_attrs(self, names):
        """ Callback to show a list of attributes. """
        if self.dev:
            (val, err) = self.fetch_values(names)
            if len(err):
                QtGui.QMessageBox.critical(
                        self._parent,
                        _trUtf8("TANGO error"),
                        _trUtf8("There was errors while reading attributes.\nErrors:\n%s") % ("\n".join(err), ))
                return

            try:
                # Remove scalar values
                for i in range(len(names) - 1, -1, -1):
                    if type(val[i]) is np.ndarray:
                        continue
                    if type(val[i]) is tuple and type(val[i][0]) is np.ndarray and type(val[i][1]) is np.ndarray:
                        continue

                    self.logger.info("Ignoring dataset '%s' of type '%s'.", names[i], type(val[i]))
                    del val[i]
                    del names[i]

                if len(val) > 0:
                    dlg = PlotDialog(names, val, self._parent)
                    dlg.show()
                    #dlg.names = names
                    self._parent.dialogs.append(dlg)
                else:
                    QtGui.QMessageBox.warning(
                                self._parent,
                                _trUtf8("Display error"),
                                _trUtf8("The selected variable cannot be plotted."))
            except Exception, e:
                self.logger.error("Got exception in show_attrs (Error: %s)", e, exc_info=True)

    def flags(self, index):
        """ Model flags. """
        flags = super(AttributeModel, self).flags(index)
        if index.isValid():
            flags |= QtCore.Qt.ItemIsEditable
            if index.column() > 3:
                flags = flags.__xor__(QtCore.Qt.ItemIsSelectable)
        return flags

    def _tango_dtype2str(self, dtype):
        """ Convert data type from TANGO to string. """
        if dtype == PT.ArgType.DevBoolean:
            return "Bool"
        elif dtype == PT.ArgType.DevUChar:
            return "Uint8"
        elif dtype == PT.ArgType.DevUShort:
            return "Uint16"
        elif dtype == PT.ArgType.DevULong:
            return "Uint32"
        elif dtype == PT.ArgType.DevULong64:
            return "Uint64"
        elif dtype == PT.ArgType.DevShort:
            return "Int16"
        elif dtype == PT.ArgType.DevLong:
            return "Int32"
        elif dtype == PT.ArgType.DevLong64:
            return "Int64"
        elif dtype == PT.ArgType.DevFloat:
            return "Float"
        elif dtype == PT.ArgType.DevDouble:
            return "Double"
        else:
            return "Unknown"

    def _tango_atype2str(self, atype):
        """ Convert attribute type from TANGO to string. """
        if atype == PT.AttrDataFormat.SCALAR:
            return "Scalar"
        elif atype == PT.AttrDataFormat.SPECTRUM:
            return "Spectrum"
        elif atype == PT.AttrDataFormat.IMAGE:
            return "Image"
        else:
            return "Unknown"


class PushButtonDelegate(QtGui.QStyledItemDelegate):

    """ Pushbutton delegate. """

    def __init__(self, cols, labels, callbacks, parent=None):
        """ Constructor. """
        # Parent constructor
        QtGui.QStyledItemDelegate.__init__(self, parent)

        self.cols = cols
        self.labels = labels
        self.callbacks = callbacks

    def createEditor(self, parent, option, index):
        """ No editor needed. Return None. """
        return None

    def paint(self, painter, option, index):
        """ Draw a pushbutton. """
        if index.column() in self.cols:

            button_style = QtGui.QStyleOptionButton()
            if index.model().data(index, QtCore.Qt.DisplayRole).toBool():
                button_style.state |= QtGui.QStyle.State_Sunken
            button_style.state |= QtGui.QStyle.State_Enabled
            button_style.rect = option.rect
            button_style.text = self.labels[self.cols.index(index.column())]
            QtGui.QApplication.style().drawControl(
                                            QtGui.QStyle.CE_PushButton,
                                            button_style,
                                            painter)
            return
        return QtGui.QStyledItemDelegate.paint(self, painter, option, index)

    def editorEvent(self, event, model, option, index):
        """ Intercept mouse clicks. """
        if index.column() in self.cols:
            if event.type() == QtCore.QEvent.MouseButtonRelease and \
                    event.button() == QtCore.Qt.LeftButton:
                # We have to reset the button
                model.setData(index, QtCore.QVariant(False), QtCore.Qt.EditRole)
                # Call callback function
                self.callbacks[self.cols.index(index.column())](model.mapToSource(index))
                return True

            elif event.type() == QtCore.QEvent.MouseButtonPress and \
                    event.button() == QtCore.Qt.LeftButton:
                # We have to draw a pushed button
                model.setData(index, QtCore.QVariant(True), QtCore.Qt.EditRole)
                return True

            elif event.type() == QtCore.QEvent.MouseButtonDblClick:
                return True

        return QtGui.QStyledItemDelegate.editorEvent(self, event, model, option, index)