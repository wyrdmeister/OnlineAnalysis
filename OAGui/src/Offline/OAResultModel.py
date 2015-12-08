# -*- coding: utf-8 -*-
"""
Online Analysis - Offline OA result model

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

import os
import inspect
import re
import h5py as h5

# PyQt
from PyQt4 import QtCore
from PyQt4 import QtGui

# Editor base
from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAOffline")

# Plot dialog
from OAGui.OAMultiplot import PlotDialog


class ResultModel(QtCore.QAbstractTableModel, GuiBase):

    """ Model for OA results. """

    def __init__(self, data, files, parent=None):
        """ Constructor. """
        # Parent constructors
        QtCore.QAbstractTableModel.__init__(self, parent)
        GuiBase.__init__(self)

        # Store parent
        self._parent = parent

        # Store data
        self._data = data
        for n in self._data.keys():
            if self._data[n].value is None:
                self.logger.debug("[%s] Removing empty dataset '%s'", inspect.stack()[0][3], n)
                del self._data[n]

        # Store files
        self._files = files

        # Get dataset names
        self._names = sorted(data.keys())

        # Button statuses
        self._bt_view = [False for n in self._names]
        self._bt_save = [False for n in self._names]

    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Return row count. """
        return len(self._names)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """ Return column count. """
        return 6

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """ Return contents of the model. """
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            val = self._data[self._names[index.row()]]
            if index.column() == 0:
                return QtCore.QVariant(val.name())

            elif index.column() == 1:
                return QtCore.QVariant(str(val.value.dtype))

            elif index.column() == 2:
                if val.name() == 'Scalar':
                    return QtCore.QVariant(str(1))
                else:
                    return QtCore.QVariant(str(val.value.shape))

            elif index.column() == 3:
                try:
                    return QtCore.QVariant(len(val.bunches))
                except:
                    return QtCore.QVariant('n.d')

            elif index.column() == 4:
                return QtCore.QVariant(self._bt_view[index.row()])

            elif index.column() == 5:
                return QtCore.QVariant(self._bt_save[index.row()])

        return QtCore.QVariant()

    def setData(self, index, data, role=QtCore.Qt.EditRole):
        """ Do nothing. This model is read-only. """
        if index.isValid():
            if index.column() == 4:
                self._bt_view[index.row()] = data.toBool()
                return True
            elif index.column() == 5:
                self._bt_save[index.row()] = data.toBool()
                return True
        return False

    def flags(self, index):
        """ Model flags. """
        flags = QtCore.QAbstractTableModel.flags(self, index)
        if index.isValid():
            if index.column() > 3:
                flags |= QtCore.Qt.ItemIsEditable
                flags &= ~QtCore.Qt.ItemIsSelectable
        return flags

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ Header data. """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return QtCore.QVariant("Attribute type")
                elif section == 1:
                    return QtCore.QVariant("Data type")
                elif section == 2:
                    return QtCore.QVariant("Size")
                elif section == 3:
                    return QtCore.QVariant("Acc.")
            elif orientation == QtCore.Qt.Vertical:
                return QtCore.QVariant(self._names[section])
        return QtCore.QVariant()

    def fetch_data(self, names):
        """ Fetch the datasets corresponding to the list of names. """
        values = []
        for n in names:
            if hasattr(self._data[n], '_x') and self._data[n]._x is not None and len(self._data[n]._x):
                values.append((self._data[n]._x, self._data[n].value))
            else:
                values.append(self._data[n].value)
        return values

    def view_dataset(self, index):
        """ Callback for saving a single value. """
        name = self._names[index.row()]
        self.view_dataset_multi([name, ])

    def view_dataset_multi(self, names):
        """ Save multiple dataset to an HDF5 file. """
        try:
            # Remove scalar values
            names = [n for n in names if self._data[n].name() != 'Scalar']
            values = self.fetch_data(names)
            if len(values) > 0:
                dlg = PlotDialog(names, values, self._parent)
                dlg.show()
                self._parent.dialogs.append(dlg)
            else:
                QtGui.QMessageBox.warning(
                            self._parent,
                            _trUtf8("Display error"),
                            _trUtf8("The selected variable cannot be plotted."))
        except Exception, e:
            self.logger.error("Got exception in show_attrs (Error: %s)", e, exc_info=True)

    def save_dataset(self, index):
        """ Callback for saving a single value. """
        name = self._names[index.row()]
        self.save_dataset_multi([name, ])

    def save_dataset_multi(self, names):
        """ Save multiple dataset to an HDF5 file. """
        # Try to open HDF5 file
        try:
            filename = unicode(QtGui.QFileDialog.getSaveFileName(
                                    self._parent,
                                    _trUtf8("Save attribute"),
                                    os.environ.get('HOME', '/home/ldm'),
                                    _trUtf8("HDF5 files (*.h5 *.hdf5)")))
            if unicode(filename) == "":
                return
            if not re.match('.*\.h5', filename):
                filename += '.h5'
            f = h5.File(str(filename), 'w')

        except Exception, e:
            self.logger.error("Failed to save data to file '%s' (Error: %s)", filename, e)
            QtGui.QMessageBox.critical(
                    self._parent,
                    _trUtf8("Error saving file"),
                    _trUtf8("Cannot open file '%s' to save data.\nError was: %s") % (filename, e))
            return

        # Save attributes
        for n in names:
            f.create_dataset(n, data=self._data[n].value)
            if hasattr(self._data[n], 'bunches') and self._data[n].bunches is not None:
                f.create_dataset(n + "__bunches", data=self._data[n].bunches)
            if hasattr(self._data[n], '_x') and self._data[n]._x is not None:
                f.create_dataset(n + "__x", data=self._data[n]._x)

        # Ask for a comment
        (comment, ok) = QtGui.QInputDialog.getText(
                                self._parent,
                                _trUtf8("Insert a comment"),
                                _trUtf8("Insert a comment in the HDF5 file. Press cancel to skip."))
        if ok and unicode(comment) != "":
            self.logger.debug("Inserted comment was: %s", comment)
            f.create_dataset("Comment", data=unicode(comment))

        # File list
        f.create_dataset("Files", data=[str(e) for e in self._files])

        # Close file
        f.close()


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
        """ No editor needed. """
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
                #self.callbacks[self.cols.index(index.column())](model.mapToSource(index))
                self.callbacks[self.cols.index(index.column())](index)
                return True

            elif event.type() == QtCore.QEvent.MouseButtonPress and \
                    event.button() == QtCore.Qt.LeftButton:
                # We have to draw a pushed button
                model.setData(index, QtCore.QVariant(True), QtCore.Qt.EditRole)
                return True

            elif event.type() == QtCore.QEvent.MouseButtonDblClick:
                return True

        return QtGui.QStyledItemDelegate.editorEvent(self, event, model, option, index)