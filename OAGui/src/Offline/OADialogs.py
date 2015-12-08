# -*- coding: utf-8 -*-
"""
Online Analysis - Offline OA dialogs

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
import re
import time
import math

# PyQt
from PyQt4 import QtCore
from PyQt4 import QtGui

# Editor base
from OAGui.GuiBase import GuiBase

# Ui
from Ui import Ui_OASelect
from Ui import Ui_OAProgress


class OASelect(QtGui.QDialog, GuiBase, Ui_OASelect):

    """ File selction dialog. """

    def __init__(self, basepath, parent=None):
        """ Constructor. """
        # Parent constructors
        QtGui.QDialog.__init__(self, parent)
        GuiBase.__init__(self, "OAOffline")

        # Build Ui
        self.setupUi(self)

        # Load file list
        (self.basepath, d, f) = os.walk(basepath).next()
        for name in f:
            if re.match('.*\.h5$', name):
                self.file_list.addItem(name)
        self.file_list.sortItems(QtCore.Qt.AscendingOrder)
        self.file_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # Output list
        self.files = []

    ##
    ## Button slots
    ##
    @QtCore.pyqtSlot()
    def on_select_button_released(self):
        """ Select all button slot. """
        model = self.file_list.model()
        selection = QtGui.QItemSelection(model.index(0, 0), model.index(model.rowCount() - 1, 0))
        self.file_list.selectionModel().reset()
        self.file_list.selectionModel().select(selection, QtGui.QItemSelectionModel.Select)

    @QtCore.pyqtSlot()
    def on_abort_button_released(self):
        """ Cancel button slot. """
        self.reject()

    @QtCore.pyqtSlot()
    def on_confirm_button_released(self):
        """ Confirm button slot. """
        self.accept()

    @QtCore.pyqtSlot()
    def accept(self):
        """ Accept routine. """
        # Store all the selected files with the basepath in self.files
        self.files = []
        for item in self.file_list.selectedItems():
            self.files.append(os.path.join(self.basepath, unicode(item.text())))
        QtGui.QDialog.accept(self)


class OAProgress(QtGui.QDialog, GuiBase, Ui_OAProgress):

    """ Progress bar dialog. """

    updateProgress = QtCore.pyqtSignal(int, unicode)

    def __init__(self, tot, parent=None):
        """ Constructor. """
        # Parent constructors
        QtGui.QDialog.__init__(self, parent)
        GuiBase.__init__(self, "OAOffline")

        # Build Ui
        self.setupUi(self)

        # Connect update
        self.updateProgress.connect(self._update)

        # Total number of files
        self.progress.setMaximum(tot)
        self.total_num.setText("%d" % (tot, ))
        self.total = tot

        # Status
        self._cancelled = False

        # Prev update
        self.start = time.time()

        # Reset progress bar
        self.progress.setValue(0)

    @QtCore.pyqtSlot(int, unicode)
    def _update(self, num, name):
        """ Update the progress dialog. """
        self.progress.setValue(num)
        self.current_num.setText("%d" % (num, ))
        (path, name) = os.path.split(unicode(name))
        self.filename.setText(name)
        tl = (self.total - num) * (time.time() - self.start) / num
        self.time_left.setText("%dm %ds" % (math.floor(tl / 60), int(tl) % 60))

    @QtCore.pyqtSlot()
    def on_abort_button_released(self):
        """ Abort button slot. """
        self._cancelled = True
        self.abort_button.setDisabled(True)

    def wasCancelled(self):
        """ Check if the operation was aborted. """
        return self._cancelled