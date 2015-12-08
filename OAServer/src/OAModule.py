# -*- coding: utf-8 -*-
"""
Online Analysis - Main module

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

import sys
from OACommon.BaseObject import BaseObject
from OACommon.Configuration import Configuration
from OACommon.Analyzer import Analyzer
from OACommon.Presenter import Presenter


class OA(BaseObject):

    """ Implement the main OA processing

    """

    def __init__(self, configfile):
        """ Constructor. """
        BaseObject.__init__(self)
        self.name("OA")
        self.version("1.0")

        # Build configuration
        self.config = Configuration(configfile)

        # Create analyzer
        self.analyzer = Analyzer(self.config)

        # Default output function
        self.outfunc = lambda data, params: data

        # Load output function
        try:
            # Import module
            __import__(self.config.output['oa']['module'])
            # Create object
            outclass = getattr(
                sys.modules[self.config.output['oa']['module']],
                self.config.output['oa']['class']
            )
            self.out = outclass(self.config.output['oa']['parameters'])
            self.outfunc = self.out.output

        except Exception as e:
            self.logger.error("[%s] Error loading the output function (Error: %s)", self.name(), e, exc_info=True)

    def process(self, filename):
        """ Take as input an HDF5 file name and return the preprocessed data. """
        data = self.analyzer.analyze(filename)

        # Purge from data all the raw data
        for k in tuple(data.keys()):
            if data[k].classtype() == 'Raw':
                del data[k]

        # Output function parameters
        params = {'filename': filename}

        # Run output function
        return self.outfunc(data, params)


class OAPresentation(BaseObject):

    """ Implements the OA presentation

    """

    def __init__(self, configfile):
        """ Constructor. """
        BaseObject.__init__(self)
        self.name("OAPresentation")
        self.version("1.0")

        # Build configuration
        self.config = Configuration(configfile)

        # Create presenter
        self.presenter = Presenter(self.config)

        # Default output function
        self.outfunc = lambda data, params: True
        self.resetfunc = lambda flags: [False for k in flags]

        # Load output function
        try:
            # Import module
            __import__(self.config.output['present']['module'])
            # Create object
            outclass = getattr(
                sys.modules[self.config.output['present']['module']],
                self.config.output['present']['class']
            )
            self.out = outclass(self.config.output['present']['parameters'])
            self.outfunc = self.out.output
            self.resetfunc = self.out.reset

        except Exception as e:
            self.logger.error("[%s] Error loading the output function (Error: %s)", self.name(), e, exc_info=True)

    def update(self, data):
        """ Update presenters. """
        # Reset presenters if needed
        self.presenter.reset(self.resetfunc)

        # Update presenters
        return self.outfunc(self.presenter.update(data), {})