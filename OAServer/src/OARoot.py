#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Online Analysis - Interface classes for the WorkSpawner

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

from OACommon.BaseObject import BaseObject
from OAModule import OA
from OAModule import OAPresentation

PyTango = None

# Default configuration file path
DEF_CONFIG_FILE = '/scratchldm/new_fermidaq/OA/OAConfig.xml'

# Get configuration file path from environment if set
CONFIG_FILE = os.environ.get('OA_CONFIG_FILE', DEF_CONFIG_FILE)


class OASingle(BaseObject):
    def __init__(self):
        BaseObject.__init__(self)
        self.name("OASingle")
        self.version("1.0")
        self.oa = OA(CONFIG_FILE)
        #global PyTango
        #import PyTango
        #self.dev = PyTango.AttributeProxy("srv-ldm-srf:20000/ldm/postprocessing/file_mover/FileToProcess")

    def process(self, filename):
        self.logger.info("[%s] Analysing file '%s'", self.name(), filename)

        # Processing file from command line
        try:
            data = self.oa.process(filename)
            #self.dev.write(filename)
            return data

        except Exception as e:
            self.logger.error("[%s] Processing failed (Error: %s)", self.name(), e, exc_info=True)
            return []


class OAPresent(BaseObject):
    def __init__(self):
        BaseObject.__init__(self)
        self.name("OAPresent")
        self.oa_presenter = OAPresentation(CONFIG_FILE)

    def update(self, data):
        self.logger.info("[%s] Starting post-processing.", self.name())
        try:
            if type(data) is dict:
                if len(data) > 0:
                    return self.oa_presenter.update(data)
                else:
                    return True
            else:
                self.logger.warning("[%s] Got invalid data of type '%s'", self.name(), type(data))
                return False

        except Exception as e:
            self.logger.error("[%s] Presenting failed (Error: %s)", self.name(), e, exc_info=True)
            return False