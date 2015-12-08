# -*- coding: utf-8 -*-
"""
Online Analysis - Base class

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

from Logger import Logger
LOG_LEVEL = Logger.DEBUG
LOG_HOST = "localhost:9999"


class BaseObject(object):

    """ Base class for all other OA objects. """

    def __init__(self):
        """ Constructor. """
        self.__name = "BaseObject"
        self.__version = "1.0"
        self.__classtype = "None"

        # Logging configuration
        self.logger = Logger(name="OA", level=LOG_LEVEL, server=LOG_HOST)

    def name(self, name=None):
        """ Set or get class name. """
        if name is not None:
            if type(name) is not str:
                self.logger.error("[%s] name must be a string", self.__name)
            else:
                self.__name = name
        return self.__name

    def version(self, name=None):
        """ Set or get class version. """
        if name is not None:
            if type(name) is not str:
                self.logger.error("[%s] version parameter must be a string", self.__name)
            else:
                self.__version = name
        return self.__version

    def classtype(self, name=None):
        """ Set or get class type. """
        if name is not None:
            if type(name) is not str:
                self.logger.error("[%s] class type parameter must be a string", self.__name)
            else:
                self.__classtype = name
        return self.__classtype