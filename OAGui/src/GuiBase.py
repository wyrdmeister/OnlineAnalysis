# -*- coding: utf-8 -*-
"""
Online Analysis Configuration Editor - Base class with logging functions

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

import argparse
import logging

from PyQt4 import QtCore
from PyQt4 import QtGui


def declare_trUtf8(name):
    """ Declare a UTF-8 translation function with the given module name. """
    def function(string):
        try:
            return unicode(QtGui.QApplication.translate(name, string, None, QtGui.QApplication.UnicodeUTF8))
        except:
            return unicode(string)
    return function


class GuiBase(QtCore.QObject):

    """ Base OA GUI class with logging facilities. """

    def __init__(self, name='OAGui'):
        """ Constructor. """
        # Parent constructor
        QtCore.QObject.__init__(self)
        # Parse command line args
        ap = argparse.ArgumentParser(prog=name, add_help=False)
        ap.add_argument('-d, --debug', dest="debug", action="store_const", const=Logger.DEBUG, default=Logger.INFO)
        out = ap.parse_args()

        # Init logger
        self.logger = Logger(name, out.debug)


class WidgetHandler(logging.Handler):

    """ Logging handler that send formatted output to QListWidget. """

    def __init__(self, signal, level=logging.NOTSET):
        """ Constructor. """
        logging.Handler.__init__(self, level)
        self._signal = signal

    def emit(self, record):
        """ Stores a record. """
        self._signal.emit(unicode(self.format(record)))


class Logger(object):

    """ Logger class. """

    def __init__(self, name="Default", level=logging.INFO):
        """ Constructor. """
        self._name = name
        self._level = level
        self._init_logger()

    def _init_logger(self):
        """ Initialize the logger object. """
        # Setup logger
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._level)

        # Add standard handler if not present
        for h in self._logger.handlers:
            try:
                if h.name == self._name + "_handler":
                    return
            except:
                pass

        _handler = logging.StreamHandler()
        _handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s:%(message)s', '%b %d, %H:%M:%S'))
        _handler.setLevel(self._level)
        _handler.name = self._name + "_handler"
        self._logger.addHandler(_handler)

    def setupWidgetLogger(self, signal):
        """ Add a widget handler to the current logger. """
        for h in self._logger.handlers:
            try:
                if h.name == self._name + "_WidgetLogger":
                    return
            except:
                pass
        handler = WidgetHandler(signal, self._level)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s:%(message)s', '%b %d, %H:%M:%S'))
        handler.name = "OAEditor_WidgetLogger"
        self._logger.addHandler(handler)

    def __getstate__(self):
        """ Enable the logger object to be pickled. """
        odict = self.__dict__.copy()  # copy the dict since we change it
        del odict['_logger']          # remove logger entry
        return odict

    def __setstate__(self, idict):
        """ Enable the logger object to be unpickled. """
        self.__dict__.update(idict)   # restore dict
        self._init_logger()

    def level(self):
        """ Return logger level. """
        return self._level

    def critical(self, msg, *args, **kwargs):
        """ Equivalent to logging.critical """
        if 'exc_info' in kwargs and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.CRITICAL, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """ Equivalent to logging.error """
        if 'exc_info' in kwargs and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.ERROR, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """ Equivalent to logging.warning """
        if 'exc_info' in kwargs and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.WARN, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """ Equivalent to logging.info """
        if 'exc_info' in kwargs and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """ Equivalent to logging.debug """
        self._logger.log(logging.DEBUG, msg, *args, **kwargs)

    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL