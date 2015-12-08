# -*- coding: utf-8 -*-
"""
Online Analysis - Analyzer class (processing entry-point)

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

try:
    import h5py
except RuntimeWarning:
    pass

from BaseObject import BaseObject
import DataObj

# SQLite benchmarking module
#import Benchmarking


class Analyzer(BaseObject):
    """ Class Analyzer
    """
    def __init__(self, config):
        """ Constructor. A valid configuration object must be passed as
        input parameter.
        """
        super(Analyzer, self).__init__()
        self.name("Analyzer")
        self.config = config

    #@Benchmarking.sqlite_profile
    def analyze(self, h5_filename):
        """ Run the analysis of an HDF5 file. A valid filename should be
        passed as the only parameter.
        """
        try:
            # Open HDF5 input file
            try:
                self.logger.debug("[%s] Loading file '%s'", self.name(), h5_filename)
                h5in = h5py.File(h5_filename, 'r')
            except IOError:
                self.logger.error("[%s] Cannot find file '%s'", self.name(), h5_filename)
                return {}

            # Load data from HDF5
            # NB: the first size of the ndarrays loaded from the HDF5 files are meant as the number of independent datasets.
            raw_data = {}

            # Import data objects
            try:
                for key in self.config.rawdata.keys():

                    try:
                        # Load all data once to optimize I/O
                        data = h5in.get(self.config.rawdata[key][1]).value
                        self.logger.debug("[%s] Loaded dataset '%s' which has type '%s'.", self.name(), key, type(data))
                    except AttributeError, e:
                        self.logger.error("[%s] Cannot find dataset '%s' (Error: %s)", self.name(), key, e)
                        continue

                    # Load HDF5 attributes
                    attrs = {}
                    for name in h5in.get(self.config.rawdata[key][1]).attrs.keys():
                        attrs[name] = h5in.get(self.config.rawdata[key][1]).attrs[name]

                    # Store data into object
                    try:
                        raw_data[key] = getattr(DataObj, self.config.rawdata[key][0])()
                        raw_data[key].load(data, attrs)
                        raw_data[key].classtype('Raw')
                    except Exception, e:
                        self.logger.error("[%s] Error creating object for dataset '%s' (Error: %s)", self.name(), key, e, exc_info=True)
                        if key in raw_data:
                            # Remove incomplete dataset
                            del raw_data[key]

                self.logger.debug("[%s] Loaded %d raw datasets.", self.name(), len(raw_data))

                # Close input HDF5 file
                h5in.close()

            except Exception, e:
                self.logger.error("[%s] Error loading datasets (Error: %s)", self.name(), e, exc_info=True)
                h5in.close()
                return {}

            # Run configured algorithms
            for algo in self.config.algorithms:
                algo[2]._process(raw_data)

            # Return all data
            return raw_data

        except Exception as e:
            self.logger.error("[%s] Unhandled exception (Error: %s)", self.name(), e, exc_info=True)
            return {}