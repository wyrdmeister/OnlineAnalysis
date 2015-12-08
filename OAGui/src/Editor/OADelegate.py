# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Editor - Visualization delegates

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


import sys
import inspect
from copy import deepcopy as copy

from PyQt4 import QtCore
from PyQt4 import QtGui

from OAGui.GuiBase import GuiBase
from OAGui.GuiBase import declare_trUtf8
_trUtf8 = declare_trUtf8("OAEditor")


class BaseDelegate(GuiBase):

    """ Base delegate class. """

    def __init__(self, parameters={}, parent=None):
        """ Constructor. """
        # Parent constructor
        GuiBase.__init__(self)
        # Parent ItemDelegate
        self.parent = parent
        # Parameter configuration
        try:
            self.configure(parameters)
        except Exception, e:
            self.logger.error("[%s] Exception while configuring delegate (Error: %s)", inspect.stack()[0][3], e)

    def configure(self, parameters):
        """ Defautl configuration function. Do nothing. """
        pass

    def _paint(self, painter, option, text):
        """ Private painting function. """
        margin = QtGui.QApplication.style().pixelMetric(QtGui.QStyle.PM_FocusFrameHMargin) + 1
        rect = QtCore.QRect(
                    option.rect.x() + margin,
                    option.rect.y(),
                    option.rect.width() - 2 * margin,
                    option.rect.height())
        painter.drawText(rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, text)

    def setModelData(self, editor, model, index):
        """ Generic setModelData. """
        (data, ok) = self.verifyEditorData(editor, index)
        if ok:
            model.setData(index, QtCore.QVariant(data), QtCore.Qt.EditRole)

    def verifyEditorData(self, editor, index):
        """ Verify the editor data. The default implementation return false. """
        return (None, False)

    def editorEvent(self, event, model, option, index):
        """ Default editor event handler. Do nothing. """
        return False

    def paint(self, painter, option, index):
        """ Default paint event handler. """
        QtGui.QStyledItemDelegate.paint(self.parent, painter, option, index)


class CheckboxDelegate(BaseDelegate):

    """ Checkbox delegate functions. """

    def createEditor(self, parent, option, index):
        """ Return None as checkbox delegate need no editor. """
        return None

    def setEditorData(self, editor, index):
        """ Set the editor data. Do nothing. """
        pass

    def verifyEditorData(self, editor, index):
        """ Toggle the checkbox value. """
        return (not index.model().data(index, QtCore.Qt.DisplayRole).toBool(), True)

    def paint(self, painter, option, index):
        """ Paint event handler. """
        # Paint a checkbox without the label
        checked = bool(index.data().toInt()[0])
        check_box_style_option = QtGui.QStyleOptionButton()
        # Checkbox style
        if index.flags() & QtCore.Qt.ItemIsEditable:
            check_box_style_option.state |= QtGui.QStyle.State_Enabled
        else:
            check_box_style_option.state |= QtGui.QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QtGui.QStyle.State_On
        else:
            check_box_style_option.state |= QtGui.QStyle.State_Off

        check_box_style_option.rect = self._getCheckBoxRect(option)
        # Draw the checkbox
        QtGui.QApplication.style().drawControl(
                                        QtGui.QStyle.CE_CheckBox,
                                        check_box_style_option,
                                        painter)

    def editorEvent(self, event, model, option, index):
        """ Intercept mouse click on the checkbox. """

        if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
            if self._getCheckBoxRect(option).contains(event.pos()):
                # The click event is inside the checkbox, so we toggle it
                self.setModelData(None, model, index)
                return True

        elif event.type() == QtCore.QEvent.MouseButtonDblClick:
            return True

        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Space or event.key() == QtCore.Qt.Key_Select:
                return True
        return False

    def _getCheckBoxRect(self, option):
        """ Service function for checkbox delegate. """
        check_box_rect = QtGui.QApplication.style().subElementRect(
                            QtGui.QStyle.SE_CheckBoxIndicator,
                            QtGui.QStyleOptionButton(),
                            None)
        check_box_point = QtCore.QPoint(
                            option.rect.x() + option.rect.width() / 2 - check_box_rect.width() / 2,
                            option.rect.y() + option.rect.height() / 2 - check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())


class ComboboxDelegate(BaseDelegate):

    """ ComboBox delegate. """

    def configure(self, parameters):
        """ Configure function. """
        try:
            self.labels = [unicode(t) for t in copy(parameters['labels'])]
        except Exception:
            self.labels = []
        try:
            self.values = [unicode(t) for t in copy(parameters['values'])]
            if len(self.values) != len(self.labels):
                raise
        except Exception:
            self.values = self.labels

        self.logger.debug("[%s] Configured a ComboBoxDelegate with %d options.", inspect.stack()[0][3], len(self.labels))

    def createEditor(self, parent, option, index):
        """ Return combobox widget. """
        editor = QtGui.QComboBox(parent)
        for i in range(len(self.labels)):
            editor.addItem(self.labels[i], self.values[i])
        #editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        """ Set the editor data. """
        currval = unicode(index.model().data(index).toString())
        for v in self.values:
            if v == currval:
                editor.setCurrentIndex(self.values.index(v))

    def verifyEditorData(self, editor, index):
        """ Return the current option. """
        return (editor.itemData(editor.currentIndex()), True)

    def paint(self, painter, option, index):
        """ Paint event handler. """
        val = unicode(index.data().toString())
        try:
            i = self.values.index(val)
            text = self.labels[i]
        except ValueError:
            text = val
        self._paint(painter, option, text)


class ComboboxDelegateID(BaseDelegate):

    """ ComboBox delegate. Options corresponds to indexes. """

    def configure(self, parameters):
        """ Configure function. """
        try:
            self.labels = copy(parameters['labels'])
        except:
            self.labels = []

    def createEditor(self, parent, option, index):
        """ Return combobox widget. """
        editor = QtGui.QComboBox(parent)
        editor.addItems(self.labels)
        #editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        """ Set the editor data. """
        currval = index.model().data(index).toInt()[0]
        editor.setCurrentIndex(currval)

    def verifyEditorData(self, editor, index):
        """ Modify the model. """
        return (editor.currentIndex(), True)

    def paint(self, painter, option, index):
        """ Paint event handler. """
        text = self.labels[index.data().toInt()[0]]
        self._paint(painter, option, text)


class ComboboxDelegateMulti(BaseDelegate):

    """ ComboBox delegate with multiple selection. """

    def configure(self, parameters):
        """ Configure function. """
        try:
            self.labels = copy(parameters['labels'])
        except:
            self.labels = []
        try:
            self.values = copy(parameters['values'])
            if len(self.values) != len(self.labels):
                raise
        except:
            self.values = self.labels

    def createEditor(self, parent, option, index):
        """ Return combobox widget. """
        # Return a checkable combobox
        # Create model
        model = QtGui.QStandardItemModel()
        # Add items
        for i in range(len(self.labels)):
            item = QtGui.QStandardItem()
            item.setText(self.labels[i])
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
            item.setData(QtCore.QVariant(self.values[i]), QtCore.Qt.EditRole)
            model.insertRow(model.rowCount(), item)
        # Create combobox
        editor = QtGui.QComboBox(parent)
        editor.setModel(model)
        editor.setItemDelegate(QtGui.QStyledItemDelegate())
        return editor

    def setEditorData(self, editor, index):
        """ Set the editor data. """
        modval = str(index.data().toString())
        if modval != "":
            # Get data
            try:
                value = eval(modval, {"__builtins__": None}, {})
            except Exception, e:
                self.logger.error("[%s] Exception while evaluating variable list (Error: %s)", inspect.stack()[0][3], e)
                value = []
            for i in range(editor.model().rowCount()):
                item = editor.model().item(i)
                if item.text() in value:
                    item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)

    def verifyEditorData(self, editor, index):
        """ Return the list of selected options. """
        outval = []
        for i in range(editor.model().rowCount()):
            item = editor.model().item(i)
            if item.checkState() == QtCore.Qt.Checked:
                outval.append(str(item.text()))
        return (unicode(outval), True)


class FramePopup(QtGui.QFrame, GuiBase):

    """ General purpose popup frame. """

    def __init__(self, parent=None):
        """ Constructor. """
        # Parent constructor
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        GuiBase.__init__(self)

        # Add base layout (to make the editor resizable and on top)
        self.layout = QtGui.QVBoxLayout(self)

        # Test counter
        self.count = 0

        # Parent delegate test function
        self.del_verify = None
        self.del_index = None

    def configureVerify(self, func, index):
        """ Configure the verification function. """
        self.del_verify = func
        self.del_index = index

    def showEvent(self, e):
        """ Intercept showEvent and move the popup in the correnct position.
        """
        p = self.parent().mapToGlobal(QtCore.QPoint(0, 0))
        self.move(p + self.pos())
        # Call parent event handler
        return QtGui.QFrame.showEvent(self, e)

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        """ Close event. """
        if self.del_verify:
            (data, ok) = self.del_verify(self, self.del_index)
            if not ok:
                event.ignore()
                return
        event.accept()


class MultiEditPopup(FramePopup):
    """ Create a popup to edit a list of variables
    """
    def __init__(self, m, n, extendable=False, parent=None):
        """ Create the popup widgets. Create the popup with mxn cells. """
        # Parent constructor
        FramePopup.__init__(self, parent)

        # Hold the line widgets
        self.lines = []

        # Layout
        lines_layout = QtGui.QGridLayout()
        self.layout.addLayout(lines_layout)

        # Create line
        for i in range(m):
            self.lines.append([])
            for j in range(n):
                l = QtGui.QLineEdit(self)
                l.setGeometry(0, 0, 50, 27)
                # Append to line list
                self.lines[i].append(l)
                # Append to layout
                lines_layout.addWidget(l, i, j)

        # Horizontal layout for buttons
        blayout = QtGui.QHBoxLayout()
        if extendable:
            # Button to add a new line
            badd = QtGui.QPushButton(_trUtf8("Add"), self)
            badd.clicked.connect(self.add)
            blayout.addWidget(badd)
        # Button to confirm (close the popup)
        bok = QtGui.QPushButton(_trUtf8("Confirm"), self)
        bok.clicked.connect(self.close)
        blayout.addWidget(bok)
        self.layout.addLayout(blayout)

    def showEvent(self, e):
        """ Intercept showEvent and move the popup in the correnct position.
        """
        p = self.parent().mapToGlobal(QtCore.QPoint(0, 0))
        self.move(p + self.pos())
        # Call parent event handler
        return QtGui.QFrame.showEvent(self, e)

    def add(self):
        """ Callback that add a new line to the popup. """
        # Add a new line of widgets to the popup
        lay = self.layout.itemAt(0).layout()
        i = lay.rowCount()
        self.lines.append([])
        for j in range(lay.columnCount()):
            l = QtGui.QLineEdit(self)
            l.setGeometry(0, 0, 50, 27)
            lay.addWidget(l, i, j)
            self.lines[i].append(l)


class MultiEditDelegate(BaseDelegate):

    """ Create a multi-line popup to conveniently edit lists of values. """

    def configure(self, parameters):
        """ Configure function. """
        try:
            self.m = copy(parameters['m'])
        except:
            self.m = None  # Unlimited number of elements
        try:
            self.n = copy(parameters['n'])
        except:
            self.n = 1

    def createEditor(self, parent, option, index):
        """ Return the multiedit popoup widget. """
        # Create main editor
        if self.m is None:
            try:
                items = eval(str(index.data().toString()), {"__builtins__": None}, {})
                if type(items) is not list or not len(items) > 0:
                    raise
                if self.n > 1 and type(items[0]) is not list:
                    raise
                m = len(items)
                if not m > 0:
                    raise
            except:
                m = 1
            finally:
                edit = MultiEditPopup(m, self.n, True, parent)
        else:
            edit = MultiEditPopup(self.m, self.n, False, parent)
        # Configure input verification
        edit.configureVerify(self.verifyEditorData, index)
        return edit

    def setEditorData(self, editor, index):
        """ Split list of values in the boxes of the multiedit popup. """
        if str(index.data().toString()) != "":
            try:
                # Eval item list
                items = eval(str(index.data().toString()), {"__builtins__": None}, {})

                if type(items) is list and len(items) > 0:
                    # Matrix of values
                    if self.n > 1:
                        if self.m is None:
                            m = len(items)
                        else:
                            m = self.m
                        for i in range(m):
                            for j in range(self.n):
                                try:
                                    editor.lines[i][j].setText(str(items[i][j]))
                                except:
                                    pass
                    # List of values
                    else:
                        if self.m is None:
                            m = len(items)
                        else:
                            m = self.m
                        for i in range(m):
                            try:
                                editor.lines[i][0].setText(str(items[i]))
                            except:
                                pass

            except Exception, e:
                self.logger.error("[%s] Cannot eval parameter value (Error: %s)", inspect.stack()[0][3], e)

    def verifyEditorData(self, editor, index):
        """ Save the multiedit popup values in the model. """
        items = []
        if self.m is None:
            # Variable number of lines
            for i in range(len(editor.lines)):
                if self.n > 1:
                    # List of lists
                    vlist = []
                    for j in range(self.n):
                        try:
                            vlist.append(eval(str(editor.lines[i][j].text()), {"__builtins__": None}, {}))
                        except:
                            if str(editor.lines[i][j].text()) == "":
                                vlist.append(None)
                            else:
                                vlist.append(str(editor.lines[i][j].text()))
                    # We add the line only if there's at least one element that is not none
                    if len(filter(lambda x: x is not None, vlist)) > 0:
                        items.append(vlist)
                else:
                    # List of values
                    if str(editor.lines[i][0].text()) != "":
                        items.append(str(editor.lines[i][0].text()))

        else:
            # Fixed number of lines
            for i in range(self.m):
                if self.n > 1:
                    items.append([])
                    for j in range(self.n):
                        try:
                            items[-1].append(eval(str(editor.lines[i][j].text()), {"__builtins__": None}, {}))
                        except:
                            if str(editor.lines[i][j].text()) == "":
                                items[-1].append(None)
                            else:
                                items[-1].append(str(editor.lines[i][j].text()))
                else:
                    if str(editor.lines[i][0].text()) == "":
                        items.append(None)
                    else:
                        items.append(str(editor.lines[i][0].text()))

        # If the array is empty we set the data to blank string
        val = str(items)
        if len(items) == 0:
            val = ''
        else:
            for i in range(len(items)):
                if type(items[i]) is list:
                    if len(filter(lambda x: x is not None, items[0])) > 0:
                        break
                elif items[i] is not None:
                    break
            else:
                val = ''
        return (val, True)


class NewLine(QtGui.QWidget):
    """ Generate a new line of a RangeInputPopup. """
    def __init__(self, parent=None, check_input=None):
        # Parent constructor
        QtGui.QWidget.__init__(self, parent)
        # Build content
        self.begin = QtGui.QLineEdit(self)
        self.begin.setGeometry(QtCore.QRect(8, 1, 51, 27))
        if check_input:
            self.begin.textEdited.connect(check_input)
        self.end = QtGui.QLineEdit(self)
        self.end.setGeometry(QtCore.QRect(62, 1, 51, 27))
        if check_input:
            self.end.textEdited.connect(check_input)
        label_1 = QtGui.QLabel(self)
        label_1.setText("(")
        label_1.setGeometry(QtCore.QRect(2, 6, 16, 17))
        label_2 = QtGui.QLabel(self)
        label_2.setText(")")
        label_2.setGeometry(QtCore.QRect(114, 6, 16, 17))
        label_3 = QtGui.QLabel(self)
        label_3.setText(",")
        label_3.setGeometry(QtCore.QRect(59, 6, 16, 17))
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.resize(121, 31)

    def sizeHint(self):
        """ Size hint. """
        return QtCore.QSize(121, 31)


class RangeInputPopup(FramePopup):

    """ Create a popup to edit a list of ranges. """

    def __init__(self, m, extendable=False, cl='range', dtype=float, parent=None):
        """ Constructor. """
        # Parent constructor
        FramePopup.__init__(self, parent)

        # Store dtype
        self.dtype = dtype

        # Store type
        self.cl = cl

        # Lines layout
        self.l_layout = QtGui.QVBoxLayout()

        # Add lines
        self.lines = []
        for i in range(m):
            ln = NewLine(self, self.check_input)
            self.l_layout.addWidget(ln)
            self.lines.append(ln)

        # Add layout
        self.layout.addLayout(self.l_layout)

        # Add buttons
        b_layout = QtGui.QHBoxLayout()
        if extendable:
            # Button to add a new line
            badd = QtGui.QPushButton(_trUtf8("Add"), self)
            badd.clicked.connect(self.add)
            b_layout.addWidget(badd)
        # Button to confirm (close the popup)
        bok = QtGui.QPushButton(_trUtf8("Confirm"), self)
        bok.clicked.connect(self.close)
        b_layout.addWidget(bok)
        # Add button to layout
        self.layout.addLayout(b_layout)

    def add(self):
        """ Add a new line. """
        # Create new line
        ln = NewLine(self, self.check_input)
        # Append to layout
        self.l_layout.addWidget(ln)
        # Append to list of lines
        self.lines.append(ln)

    @QtCore.pyqtSlot(QtCore.QString)
    def check_input(self, text):
        """ Verify input. """
        # Cycle over lines
        for ln in self.lines:
            begin = str(ln.begin.text())
            end = str(ln.end.text())
            if begin == "" and end == "":
                # If the line is empty we skip it
                continue
            try:
                # Eval begin value
                begin = eval(begin, {"__builtins__": None}, {})
                if type(begin) is not self.dtype:
                    # Types differ
                    if type(begin) is float and self.dtype is int:
                        # If input data is float but int is required trigger error
                        raise
                # Eval end value
                if self.cl != 'incomplete' or end != "":
                    end = eval(end, {"__builtins__": None}, {})
                    if type(end) is not self.dtype:
                        if type(end) is float and self.dtype is int:
                            # If input data is float but int is required trigger error
                            raise
                # Trigger error also if end is not bigger than begin
                if self.cl == 'range' and end <= begin:
                    raise
                # No error. Remove red border
                ln.begin.setStyleSheet("")
                ln.end.setStyleSheet("")
            except:
                # Error detected. Set red border around input fields.
                ln.begin.setStyleSheet("border: 2px solid red")
                ln.end.setStyleSheet("border: 2px solid red")


class RangeInputDelegate(BaseDelegate):

    """ Delegate to insert an list of ranges. """

    def configure(self, parameters):
        """ Configuration routine. """
        # Check number of lines
        if 'm' in parameters:
            self.m = parameters['m']
        else:
            self.m = None
        # Check data type
        if 'dtype' in parameters:
            try:
                dt = parameters['dtype'].split(">")
                assert(dt[0] == 'list')
                if self.m is None or self.m > 1:
                    assert(dt[1] == 'list')
                if dt[-1] == 'int':
                    self.dtype = int
                else:
                    raise
            except:
                self.dtype = float
        else:
            self.dtype = float
        # Type of range
        if 'class' in parameters:
            if parameters['class'] == 'point':
                self.cl = 'point'
            elif parameters['class'] == 'incomplete':
                self.cl = 'incomplete'
            else:
                self.cl = 'range'
        else:
            self.cl = 'range'

    def createEditor(self, parent, option, index):
        """ Return a range editor. """
        # Create frame
        if self.m == None:
            try:
                # Eval input data
                items = eval(str(index.data().toString()), {"__builtins__": None}, {})
                assert(type(items) is list)
                assert(len(items) > 0)
                for i in items:
                    assert(type(i) is list)
                    assert(len(i) == 2)
                m = len(items)
            except:
                # In case of error default to one line (typically happens when the field is empty)
                m = 1
            # Create extendable popup
            edit = RangeInputPopup(m, True, self.cl, self.dtype, parent)
        else:
            # Create fixed popup
            edit = RangeInputPopup(self.m, False, self.cl, self.dtype, parent)
        # Configure input verification
        edit.configureVerify(self.verifyEditorData, index)
        return edit

    def setEditorData(self, editor, index):
        """ Split list of values in the boxes of the multiedit popup. """
        if str(index.data().toString()) != "":
            try:
                # Eval item list
                items = eval(str(index.data().toString()), {"__builtins__": None}, {})
                assert(type(items) is list)
                if self.m is None or self.m > 1:
                    assert(len(items) > 0)

                    for i in range(len(items)):
                        if i < len(editor.lines) and len(items[i]) == 2:
                            editor.lines[i].begin.setText(str(items[i][0]))
                            editor.lines[i].end.setText(str(items[i][1]))
                else:
                    editor.lines[0].begin.setText(str(items[0]))
                    editor.lines[0].end.setText(str(items[1]))
            except:
                pass

    def verifyEditorData(self, editor, index):
        """ Verification routine. """
        items = []
        # Cycle over lines
        for ln in editor.lines:
            if str(ln.begin.text()) == "" and str(ln.end.text()) == "":
                # Ignore empty lines
                continue

            try:
                # Eval input data
                el = [self.dtype(str(ln.begin.text())), ]
                if str(ln.end.text()) != "":
                    el.append(self.dtype(str(ln.end.text())))
                else:
                    if self.cl != 'incomplete':
                        raise
                if self.cl == 'range' and el[0] >= el[1]:
                    # Trigger error if begin is greater that end
                    raise
                # No errors found. Append.
                items.append(el)
            except:
                # Error. Return false
                return ("", False)

        if len(items) == 0:
            # No items. Return an empty string.
            return ("", True)
        elif self.m == 1:
            # One items. Return a simple list
            return (str(items[0]), True)
        else:
            # Return a list of lists
            return (str(items), True)


class AOIFrame(FramePopup):

    """ Frame popup for AOI input. """

    def __init__(self, parent):
        """ Constructor. """
        # Parent constructor
        FramePopup.__init__(self, parent)

        # Add layout
        grid = QtGui.QGridLayout()
        self.layout.addLayout(grid)

         # Add widgets
        label_xmin = QtGui.QLabel("X min.:")
        label_xmin.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        grid.addWidget(label_xmin, 0, 0)
        self.xmin = QtGui.QLineEdit()
        self.xmin.setGeometry(0, 0, 40, 27)
        self.xmin.textEdited.connect(self.check_input)
        grid.addWidget(self.xmin, 0, 1)

        label_xmax = QtGui.QLabel("X max.:")
        label_xmax.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        grid.addWidget(label_xmax, 0, 2)
        self.xmax = QtGui.QLineEdit()
        self.xmax.setGeometry(0, 0, 40, 27)
        self.xmax.textEdited.connect(self.check_input)
        grid.addWidget(self.xmax, 0, 3)

        label_ymin = QtGui.QLabel("Y min.:")
        label_ymin.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        grid.addWidget(label_ymin, 1, 0)
        self.ymin = QtGui.QLineEdit()
        self.ymin.setGeometry(0, 0, 40, 27)
        self.ymin.textEdited.connect(self.check_input)
        grid.addWidget(self.ymin, 1, 1)

        label_ymax = QtGui.QLabel("Y max.:")
        label_ymax.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        grid.addWidget(label_ymax, 1, 2)
        self.ymax = QtGui.QLineEdit()
        self.ymax.setGeometry(0, 0, 40, 27)
        self.ymax.textEdited.connect(self.check_input)
        grid.addWidget(self.ymax, 1, 3)

    @QtCore.pyqtSlot(QtCore.QString)
    def check_input(self, text):
        """ Verify input. """
        if int(self.xmin.text()) >= int(self.xmax.text()):
            self.xmin.setStyleSheet("border: 2px solid red")
            self.xmax.setStyleSheet("border: 2px solid red")
        else:
            self.xmin.setStyleSheet("")
            self.xmax.setStyleSheet("")
        if int(self.ymin.text()) >= int(self.ymax.text()):
            self.ymin.setStyleSheet("border: 2px solid red")
            self.ymax.setStyleSheet("border: 2px solid red")
        else:
            self.ymin.setStyleSheet("")
            self.ymax.setStyleSheet("")


class AOIDelegate(BaseDelegate):

    """ Delegate to insert an area of interest. """

    def createEditor(self, parent, option, index):
        """ Return AOI editor. """
        # Create frame
        edit = AOIFrame(parent)
        edit.configureVerify(self.verifyEditorData, index)
        return edit

    def setEditorData(self, editor, index):
        """ Populate editor. """
        try:
            val = eval(str(index.data().toString()), {"__builtins__": None}, {})
            if type(val) is list and len(val) == 4:
                editor.xmin.setText(str(val[0]))
                editor.xmax.setText(str(val[1]))
                editor.ymin.setText(str(val[2]))
                editor.ymax.setText(str(val[3]))
        except:
            pass

    def verifyEditorData(self, editor, index):
        """ Save data to model. """
        try:
            xmin = int(editor.xmin.text())
            xmax = int(editor.xmax.text())
            ymin = int(editor.ymin.text())
            ymax = int(editor.ymax.text())

            if xmax > xmin and ymax > ymin:
                aoi = [xmin, xmax, ymin, ymax]
                return (str(aoi), True)

        except:
            pass
        return ('', False)


class MassCalibrationPopup(FramePopup):

    """ Popup for mass calibration input. """

    def __init__(self, parent=None):
        """ Constructor. """
        FramePopup.__init__(self, parent)

        self._container = CalibrationEditor(self)

        # Add container to layout
        self.layout.addWidget(self._container)

        # Expose lineedits
        self.t0 = self._container.t0
        self.tk = self._container.tk

        # Add onEdit callback
        self.t0.textEdited.connect(self.check_input)
        self.tk.textEdited.connect(self.check_input)

    @QtCore.pyqtSlot(QtCore.QString)
    def check_input(self, text):
        """ Verify input. """
        try:
            if str(self.t0.text()) != "":
                t0 = float(str(self.t0.text()))
            self.t0.setStyleSheet("")
        except:
            self.t0.setStyleSheet("border: 2px solid red")
        try:
            if str(self.tk.text()) != "":
                tk = float(str(self.tk.text()))
                assert(tk != 0)
            self.tk.setStyleSheet("")
        except:
            self.tk.setStyleSheet("border: 2px solid red")


class CalibrationEditor(QtGui.QWidget):

    """ Calibration editor. """

    def __init__(self, parent=None):
        """ Constructor. """
        # Paraent constructor
        QtGui.QWidget.__init__(self, parent)
        self.resize(self.sizeHint())
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        self.t0 = QtGui.QLineEdit(self)
        self.t0.setGeometry(QtCore.QRect(87, 16, 71, 27))

        self.tk = QtGui.QLineEdit(self)
        self.tk.setGeometry(QtCore.QRect(67, 49, 81, 27))

        self._line = QtGui.QFrame(self)
        self._line.setGeometry(QtCore.QRect(58, 38, 101, 16))
        self._line.setFrameShadow(QtGui.QFrame.Plain)
        self._line.setLineWidth(2)
        self._line.setMidLineWidth(2)
        self._line.setFrameShape(QtGui.QFrame.HLine)
        self._line.setFrameShadow(QtGui.QFrame.Plain)

        self._label1 = QtGui.QLabel(self)
        self._label1.setGeometry(QtCore.QRect(39, -6, 21, 91))
        font = QtGui.QFont()
        font.setPointSize(50)
        font.setKerning(False)
        self._label1.setFont(font)
        self._label1.setScaledContents(True)
        self._label1.setText("{")
        self._label1.setStyleSheet("font-weight: 100")

        self._label2 = QtGui.QLabel(self)
        self._label2.setGeometry(QtCore.QRect(162, -7, 21, 91))
        font = QtGui.QFont()
        font.setPointSize(50)
        font.setKerning(False)
        self._label2.setFont(font)
        self._label2.setText("}")
        self._label2.setStyleSheet("font-weight: 100")

        self._label3 = QtGui.QLabel(self)
        self._label3.setGeometry(QtCore.QRect(177, 2, 16, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setKerning(False)
        self._label3.setFont(font)
        self._label3.setText("2")

        self._label4 = QtGui.QLabel(self)
        self._label4.setGeometry(QtCore.QRect(62, 21, 31, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setKerning(False)
        self._label4.setFont(font)
        self._label4.setText("t -")

        self._label5 = QtGui.QLabel(self)
        self._label5.setGeometry(QtCore.QRect(7, 35, 31, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setKerning(False)
        self._label5.setFont(font)
        self._label5.setText("m = ")

    def sizeHint(self):
        return QtCore.QSize(191, 81)


class MassCalibrationDelegate(BaseDelegate):

    """ Delegate to insert mass calibration parameters. """

    def createEditor(self, parent, option, index):
        """ Return AOI editor. """
        # Create frame
        edit = MassCalibrationPopup(parent)
        edit.configureVerify(self.verifyEditorData, index)
        return edit

    def setEditorData(self, editor, index):
        """ Populate editor. """
        try:
            val = eval(str(index.data().toString()), {"__builtins__": None}, {})
            assert(type(val) is list)
            assert(len(val) == 2)
            for v in val:
                assert(type(v) in (float, int))

            editor.t0.setText(str(val[0]))
            editor.tk.setText(str(val[1]))
        except:
            pass

    def verifyEditorData(self, editor, index):
        """ Save data to model. """
        try:
            if str(editor.t0.text()) == "" and str(editor.tk.text()) == "":
                return ("", True)
            t0 = float(editor.t0.text())
            tk = float(editor.tk.text())
            assert(tk != 0)
            return (str([t0, tk]), True)
        except:
            pass
        return ('', False)


class NullDelegate(BaseDelegate):

    """ Null delegate. Read-only delegate. """

    def createEditor(self, parent, option, index):
        return None

    def setEditorData(self, editor, index):
        pass


class ColumnDelegate(QtGui.QStyledItemDelegate, GuiBase):

    """ Configure delegates column-wise. """

    def __init__(self, parameters, parent=None):
        """ Constructor. """
        # Parent constructors
        QtGui.QStyledItemDelegate.__init__(self, parent)
        GuiBase.__init__(self)

        # Column delegate configuration
        self.cols = []
        self.delegates = []

        for p in parameters:
            try:
                dtype = getattr(sys.modules[__name__], p['type'])
                d = dtype(p, self)
                c = p['column']
                self.cols.append(c)
                self.delegates.append(d)
            except Exception, e:
                self.logger.error("[%s] There was an error initializing delegate of type '%s' (Error: %s)", inspect.stack()[0][3], p['type'], e)

    def createEditor(self, parent, option, index):
        if index.isValid() and index.column() in self.cols:
            return self.delegates[self.cols.index(index.column())].createEditor(parent, option, index)
        # Return default editor
        return QtGui.QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        if index.isValid() and index.column() in self.cols:
            self.delegates[self.cols.index(index.column())].setEditorData(editor, index)
            return
        # Default setEditorData
        QtGui.QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if index.isValid() and index.column() in self.cols:
            self.delegates[self.cols.index(index.column())].setModelData(editor, model, index)
            return
        # Run default function
        QtGui.QStyledItemDelegate.setModelData(self, editor, model, index)

    def paint(self, painter, option, index):
        if index.isValid() and index.column() in self.cols:
            self.delegates[self.cols.index(index.column())].paint(painter, option, index)
            return
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)

    def editorEvent(self, event, model, option, index):
        if index.isValid() and index.column() in self.cols:
            return self.delegates[self.cols.index(index.column())].editorEvent(event, model, option, index)
        return False


class CellDelegate(QtGui.QStyledItemDelegate, GuiBase):

    """ Configure delegates cell-wise. """

    def __init__(self, parameters, parent=None):
        """ Constructor. """
        # Parent constructors
        QtGui.QStyledItemDelegate.__init__(self, parent)
        GuiBase.__init__(self)

        # Cells
        self.cells = []
        self.delegates = []

        for p in parameters:
            try:
                dtype = getattr(sys.modules[__name__], p['name'])
                d = dtype(p, self)
                c = p['cell']
                self.cells.append(c)
                self.delegates.append(d)
                self.logger.debug("[%s] Configured delegate %s for cell %s.", inspect.stack()[0][3], p['name'], p['cell'])
            except Exception, e:
                self.logger.error("[%s] There was an error initializing delegate of type '%s' (Error: %s)", inspect.stack()[0][3], p['name'], e)

    def createEditor(self, parent, option, index):
        c = (index.row(), index.column())
        if index.isValid() and c in self.cells:
            return self.delegates[self.cells.index(c)].createEditor(parent, option, index)

        # Return default editor
        return QtGui.QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        c = (index.row(), index.column())
        if index.isValid() and c in self.cells:
            self.delegates[self.cells.index(c)].setEditorData(editor, index)
            return
        # Default setEditorData
        QtGui.QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        c = (index.row(), index.column())
        if index.isValid() and c in self.cells:
            self.delegates[self.cells.index(c)].setModelData(editor, model, index)
            return
        # Run default function
        QtGui.QStyledItemDelegate.setModelData(self, editor, model, index)

    def paint(self, painter, option, index):
        c = (index.row(), index.column())
        if index.isValid() and c in self.cells:
            self.delegates[self.cells.index(c)].paint(painter, option, index)
            return
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)

    def editorEvent(self, event, model, option, index):
        c = (index.row(), index.column())
        if index.isValid() and c in self.cells:
            return self.delegates[self.cells.index(c)].editorEvent(event, model, option, index)
        return False