# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Editor - Led widget

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

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtSvg

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class QLed(QtGui.QWidget):

    """ Draw a green/red circular LED. """

    def __init__(self, default=False, parent=None):
        """ Constructor. """
        QtGui.QWidget.__init__(self, parent)

        self.renderer = QtSvg.QSvgRenderer()

        self._onled = _fromUtf8(":/leds/greenLed")
        self._offled = _fromUtf8(":/leds/redLed")

        self._value = default

    def setValue(self, val):
        """ Set led status. """
        if val:
            self._value = True
        else:
            self._value = False
        self.update()

    @QtCore.pyqtSlot(QtGui.QPaintEvent)
    def paintEvent(self, event):
        """ Paint event handler. """
        if self._value:
            self.renderer.load(self._onled)
        else:
            self.renderer.load(self._offled)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.renderer.render(painter)