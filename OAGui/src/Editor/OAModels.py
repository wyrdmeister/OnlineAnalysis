# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Editor - Data models

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


import inspect

from PyQt4 import QtCore
from PyQt4 import QtGui

from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAEditor")


class ConfigTableModel(QtCore.QAbstractTableModel, GuiBase):

    """ TableModel to represent configuration elements. """

    def __init__(self, source, options, parent=None, *args):
        """ Constructor. """
        # Parent constructors
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        GuiBase.__init__(self)

        # Store parent
        self._parent = parent

        # Source
        self._source = source

        # Parameters
        self._cols = options

        self.logger.debug("[%s] Source contains %d elements.", inspect.stack()[0][3], len(self._source))

    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Model row count. """
        return len(self._source)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """ Model column count. """
        return len(self._cols)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """ Return model data. """
        if index.isValid() and index.column() < len(self._cols) and (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
            return QtCore.QVariant(self._source[index.row()][self._cols[index.column()]['id']])
        return QtCore.QVariant()

    def setData(self, index, data, role=QtCore.Qt.EditRole):
        """ Set model data. """
        # Check that index is valid and that we are in edit role
        if index.isValid() and index.column() < len(self._cols) and role == QtCore.Qt.EditRole:

            # If the column value should be unique we check that is not duplicated
            if self._cols[index.column()]['unique']:
                for r in range(self.rowCount()):
                    if r != index.row() and self.index(r, index.column()).data() == data:
                        QtGui.QMessageBox.critical(
                                    None,
                                    _trUtf8("Wrong value"),
                                    _trUtf8("Value of column '%s' must be unique.") % (self.headerData(index.column(), QtCore.Qt.Horizontal).toString(), ))
                        return False

            if self._cols[index.column()]['dtype'] is int:
                self._source[index.row()][self._cols[index.column()]['id']] = data.toInt()[0]
            elif self._cols[index.column()]['dtype'] is float:
                self._source[index.row()][self._cols[index.column()]['id']] = data.toDouble()[0]
            elif self._cols[index.column()]['dtype'] is bool:
                self._source[index.row()][self._cols[index.column()]['id']] = data.toBool()
            else:
                self._source[index.row()][self._cols[index.column()]['id']] = unicode(data.toString())
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        """ Return model flags. """
        # Standard flags
        fl = QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        # Special flag for checkbox delegate
        if index.data().type() == QtCore.QMetaType.Bool:
            fl &= ~QtCore.Qt.ItemIsSelectable
        return fl

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ Output column headers. """
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section < len(self._cols) and self._cols[section]['name'] != "":
                return QtCore.QVariant(self._cols[section]['name'])

        return QtCore.QVariant()

    def addElement(self, data):
        """ Add a new element. """
        if 'name' not in data and 'operator' not in data:
            # Need to have at least name or operator (for filters)
            return
        if 'type' not in data:
            # Need to have type
            return
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self._source.append(data)
        self.endInsertRows()

    def removeElement(self, index):
        """ Remove an element. """
        if type(index) is QtCore.QModelIndex:
            index = index.row()
        self.beginRemoveRows(QtCore.QModelIndex(), index, index)
        del self._source[index]
        self.endRemoveRows()


class ConfigParameterModel(QtCore.QAbstractTableModel, GuiBase):

    """ TableModel to represent algorithms and presenters parameters. """

    def __init__(self, source, options, index, parent=None):
        """ Constructor. """
        # Parent constructors
        QtCore.QAbstractTableModel.__init__(self, parent)
        GuiBase.__init__(self)

        # Store parent
        self._parent = parent

        # Store algo index
        self._index = index

        # Parameters
        self._config = options

        # Source
        self._source = source
        self._names = source.keys()

        # Update parameters
        self.updateParams()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Model row count. """
        return len(self._source)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """ Model column count. """
        return 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """ Return model data. """
        if index.isValid() and (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
            return QtCore.QVariant(self._source[self._names[index.row()]]['value'])
        return QtCore.QVariant()

    def setData(self, index, data, role=QtCore.Qt.EditRole):
        """ Set model data. """
        # Check that index is valid and that we are in edit role
        if index.isValid() and role == QtCore.Qt.EditRole:
            (dt, ok) = self._checkDType(index.row(), data)
            if ok:
                self._source[self._names[index.row()]]['value'] = dt
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        """ Return model flags. """
        # Standard flags
        fl = QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        try:
            if self._config[self._names[index.row()]]['dtype'] == 'bool':
                fl &= ~QtCore.Qt.ItemIsSelectable
        except:
            pass
        return fl

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ Output column headers. """
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Vertical:
            if section < len(self._names):
                try:
                    return QtCore.QVariant(self._config[self._names[section]]['label'])
                except:
                    return QtCore.QVariant(self._names[section])

        return QtCore.QVariant()

    def updateParams(self):
        """ Check configured parameters for consistency. Remove old parameters
        and add new ones. """
        # Remove old parameters
        for p in self._source.keys():
            if p not in self._config:
                self.logger.debug("[%s] Removing old parameter '%s'.", inspect.stack()[0][3], p)
                del self._source[p]
                self._names.remove(p)

        for p in self._config:
            # Add new ones
            if p not in self._source:
                self.logger.debug("[%s] Adding new parameter '%s'.", inspect.stack()[0][3], p)
                self._names.append(p)
                self._source[p] = {}
                self._source[p]['type'] = self._config[p]['type']
                if 'default' in self._config[p]:
                    self._source[p]['value'] = self._config[p]['default']
                else:
                    self._source[p]['value'] = ''
            # Check old ones
            else:
                # Check type
                if self._config[p]['type'] != self._source[p]['type']:
                    self.logger.warning("[%s] Found parameter '%s' with wrong type '%s'. Resetting value.", inspect.stack()[0][3], p, self._source[p]['type'])
                    self._source[p]['type'] = self._config[p]['type']
                    self._source[p]['value'] = ""
                # Parse value
                dt = self._config[p]['dtype'].split(">")
                if len(dt) == 1:
                    # We parse the values only for single values
                    if dt[0] == 'int':
                        try:
                            self._source[p]['value'] = int(self._source[p]['value'])
                        except:
                            self._source[p]['value'] = 0
                    elif dt[0] == 'num':
                        try:
                            self._source[p]['value'] = float(self._source[p]['value'])
                        except:
                            self._source[p]['value'] = 0.0
                    elif dt[0] == 'bool':
                        try:
                            self._source[p]['value'] = bool(int(self._source[p]['value']))
                        except:
                            self._source[p]['value'] = False
        # Resort parameters
        self._names = sorted(self._names, key=lambda k: self._config[k]['label'])

    def resortDelegates(self, options, variables=[]):
        """ Resort delegates definitions to match parameters order. """
        out = []
        for n in self._names:
            try:
                el = {'cell': (self._names.index(n), 0), 'type': options[n]['type'], 'dtype': options[n]['dtype']}
                if options[n]['type'] == 'var':
                    dt = options[n]['dtype'].split('>')
                    if len(dt) > 1 and dt[0] == 'list':
                        el['name'] = 'ComboboxDelegateMulti'
                        el['labels'] = variables
                        el['values'] = variables
                    else:
                        el['name'] = 'ComboboxDelegate'
                        el['labels'] = variables
                        el['values'] = variables
                    out.append(el)

                elif options[n]['type'] == 'outvar':
                    if options[n]['delegate'] is None:
                        dt = options[n]['dtype'].split('>')
                        if len(dt) > 1 and dt[0] == 'list':
                            el['name'] = 'MultiEditDelegate'
                            el['m'] = None
                            el['n'] = 1
                            out.append(el)
                    else:
                        for k in options[n]['delegate']:
                            el[k] = options[n]['delegate'][k]
                        out.append(el)

                else:
                    if options[n]['delegate'] is not None:
                        el['name'] = options[n]['delegate']['type']
                        for k in options[n]['delegate']:
                            if k != 'type':
                                el[k] = options[n]['delegate'][k]
                        out.append(el)

            except Exception, e:
                self.logger.error("[%s] Error scanning delegates (Error: %s)", inspect.stack()[0][3], e)
        return out

    def _checkDType(self, i, data):
        """ Check that the data type of the input data match the required one. """
        # Get parameter configuration
        opt = self._config[self._names[i]]

        # Output variables for an algorithm
        if opt['type'] == 'outvar':

            # Convert data to string
            data = unicode(data.toString())

            # If string is empty return directly
            # (empty output is ok for configuration purposes)
            if data == u"":
                return (data, True)

            # Split data type
            dt = opt['dtype'].split(">")
            if dt[0] == 'list':
                try:
                    items = eval(data, {"__builtins__": None}, {})
                    assert(type(items) is list)
                except:
                    return (u"", False)
            else:
                items = [data]

            # Check that there are no duplicate in our own output names
            try:
                # Inside this same paramters
                assert(len(items) == len(set(items)))
                # Inside other parameters
                for n, v in self._source.iteritems():
                    if self._names[i] == n:
                        continue
                    if self._config[n]['type'] == 'outvar':
                        dt = self._config[n]['dtype'].split(">")
                        if dt[0] == 'list':
                            try:
                                val = eval(v['value'], {"__builtins__": None}, {})
                                assert(type(val) is list)
                            except:
                                continue
                        else:
                            val = [v['value']]
                        for name in items:
                            if name in val:
                                raise

            except:
                QtGui.QMessageBox.critical(
                            self._parent,
                            _trUtf8("Duplicate name"),
                            _trUtf8("The output variables of the algorithm have a duplicate name inside."))
                return (u"", False)

            # For each items check if it already exist
            for name in items:
                if not self._parent.config.checkUniqueAlgo(self._index, name):
                    # Already in use
                    QtGui.QMessageBox.critical(
                            self._parent,
                            _trUtf8("Duplicate name"),
                            _trUtf8("The variable name '%s' is already in use.") % (name, ))
                    return (u"", False)
            # No errors
            return (data, True)

        # Output variables for a presenter
        elif opt['type'] == 'tango':

            # Convert data to string
            data = unicode(data.toString())

            # If string is empty return directly
            # (empty output is ok for configuration purposes)
            if data == u"":
                return (data, True)

            # Split data type
            dt = opt['dtype'].split(">")
            if dt[0] == 'list':
                try:
                    items = eval(data, {"__builtins__": None}, {})
                    assert(type(items) is list)
                except:
                    return (u"", False)
            else:
                items = [data]

            # Check that there are no duplicate in our own output names
            try:
                # Inside this same parameters
                assert(len(items) == len(set(items)))
                # Inside other parameters
                for n, v in self._source.iteritems():
                    if self._names[i] == n:
                        continue
                    if self._config[n]['type'] == 'tango':
                        dt = self._config[n]['dtype'].split(">")
                        if dt[0] == 'list':
                            try:
                                val = eval(v['value'], {"__builtins__": None}, {})
                                assert(type(val) is list)
                            except:
                                continue
                        else:
                            val = [v['value']]
                        for name in items:
                            if name in val:
                                raise

            except:
                QtGui.QMessageBox.critical(
                            self._parent,
                            _trUtf8("Duplicate name"),
                            _trUtf8("The output variables of the presenter have a duplicate name inside."))
                return (u"", False)

            # For each items check if it already exist
            for name in items:
                if not self._parent.config.checkUniquePres(self._index, name):
                    # Already in use
                    QtGui.QMessageBox.critical(
                            self._parent,
                            _trUtf8("Duplicate name"),
                            _trUtf8("The output TANGO name '%s' is already in use.") % (name, ))
                    return (u"", False)
            # No errors
            return (data, True)

        else:
            # Split data type
            dt = opt['dtype'].split(">")

            if len(dt) == 1:
                # Single value
                try:
                    if dt[0] == 'str':
                        return (unicode(data.toString()), True)
                    elif dt[0] == 'int':
                        (val, ok) = data.toInt()
                        if ok:
                            return (int(val), True)
                        else:
                            return (0, False)
                    elif dt[0] in ('num', 'float'):
                        (val, ok) = data.toFloat()
                        if ok:
                            return (float(val), True)
                        else:
                            return (0.0, False)
                    elif dt[0] == 'bool':
                        return (data.toBool(), True)
                    else:
                        self.logger.warning("[%s] Unrecognized data type '%s'. QVariant was of type '%s'.", dt[0], data.typeName())
                        return ("", False)
                except Exception, e:
                    self.logger.error("[%s] Error parsing input data (Error: %s, QVariant type: '%s')", inspect.stack()[0][3], e, data.typeName())
                    return ("", False)

            elif len(dt) > 1:
                try:
                    # Convert to string
                    data = unicode(data.toString())
                    # If the string is empty we just return
                    if data == u"":
                        return (u"", True)
                    # Eval item list
                    items = eval(data, {"__builtins__": None}, {})
                    if self._check_recursive(items, dt[0], dt[1:]):
                        return (data, True)
                    else:
                        return (u"", False)
                except Exception, e:
                    self.logger.warning("[%s] Error parsing data (Error: %s)", inspect.stack()[0][3], e)
                    return (u"", False)
            else:
                self.logger.warning("[%s] Bad data type '%s'.", inspect.stack()[0][3], opt['dtype'])
                return (u"", False)

    def _check_recursive(self, el, tp, other):
        self.logger.debug("[%s] Element type: %s, Expected type: %s, Other: %s.", inspect.stack()[0][3], type(el), tp, other)
        if tp == 'list':
            if type(el) is not list:
                return False
            if len(other) > 0:
                retval = True
                for e in el:
                    retval &= self._check_recursive(e, other[0], other[1:])
                return retval
            else:
                self.logger.warning("[%s] List type without element specification.", inspect.stack()[0][3])
                return True
        elif tp == 'str':
            if type(el) not in (str, unicode):
                return False
            else:
                return True
        elif tp == 'int':
            if type(el) not in (int, long):
                return False
            else:
                return True
        elif tp == 'num':
            if type(el) not in (int, long, float):
                return False
            else:
                return True
        elif tp == 'bool':
            if type(el) not in (bool, int):
                return False
            else:
                return True
        else:
            # Unknown type
            self.logger.warning("[%s] Unknown type '%s'.", inspect.stack()[0][3], tp)
            return False


class ComboboxModel(QtCore.QAbstractListModel, GuiBase):

    """ Model for comboboxes """

    def __init__(self, source, parent=None):
        """ Constructor. """
        # Parent constructors
        QtCore.QAbstractListModel.__init__(self, parent)
        GuiBase.__init__(self)

        # Source
        self._source = source

    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Model row count. """
        return len(self._source)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """ Model column count. """
        return 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """ Return value. """
        if index.isValid():
            return QtCore.QVariant(self._source[index.row()][1])

    def setData(self, index, data, role=QtCore.Qt.EditRole):
        """ Set value. """
        if index.isValid() and role == QtCore.Qt.EditRole:
            self._source[index.row()][1] = unicode(data.toString())
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        """ Return model flags. """
        # Standard flags
        fl = QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        return fl

    def insertRow(self, row, parent=QtCore.QModelIndex()):
        """ Insert one row. """
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        """ Insert multiple rows. """
        if row >= 0 and row <= self.rowCount() and count > 0:
            self.beginInsertRows(parent, row, row + count - 1)
            for i in range(count):
                self._source.insert(row + i, [False, ''])
            self.endInsertRows()
            return True
        return False