# -*- coding: utf-8 -*-
"""
Online Analysis - Processing output classes

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
import numpy as np
from OACommon.BaseObject import BaseObject
h5py = None


class OA2HDF(BaseObject):

    """ Save the output of the OA to an HDF5 file. """

    def __init__(self, params):
        """ Constructor. """
        super(OA2HDF, self).__init__()
        self.name("OA2HDF")
        self.version("1.0")

        # Conditionally import H5PY
        global h5py
        import h5py

        # Get module parameters
        try:
            self.re = re.compile(params['path_re'])
            self.outpath = params['outpath']
            self.enable = True
        except Exception, e:
            self.logger.error("[%s] Error while initializing output module. Disabling. (Error: %s)", self.name(), e)
            self.enable = False

    def output(self, data, params):
        # If the module is enabled
        if self.enable:
            # Check for filename
            if 'filename' not in params:
                self.logger.error("[%s] missing filename parameter.", self.name())
                return data

            # Check if there's anything to save
            res = [data[0][k].classtype == 'Result' for k in data[0].keys()]
            if not any(res):
                # Nothing to save
                return data

            # Create output filename
            try:
                h5_outname = self.re.sub(params['outpath'], os.path.dirname(params['filename'])) + "/OA_" + os.path.basename(params['filename'])
            except Exception, e:
                self.logger.error("[%s] Error formatting output filename (Error: %s)", self.name(), e)
                return data

            # Create output directory if it does not exist
            if not os.path.isdir(os.path.dirname(h5_outname)):
                os.makedirs(os.path.dirname(h5_outname))

            self.logger.debug("[%s] Saving OA output to file '%s'", self.name(), h5_outname)

            # Open output HDF5 file
            try:
                out = h5py.File(h5_outname, mode='w')
            except IOError as e:
                self.logger.error("[%s] Cannot create HDF5 file '%s' (Error: %s)", self.name(), h5_outname, e)
                return data

            # NB: all the data sets should have the same elements
            # This way we can merge all the elements of one type in a single dataset
            for k in data[0].keys():
                if data[0][k].classtype() == "Result":
                    outd = []
                    for dset in data:
                        outd.append(dset[k].value)
                    out.create_dataset(k, data=np.array(outd))

            # Close output file
            out.close()

        # Return results
        return data


class NoOut(BaseObject):

    """ Noop output class """

    def __init__(self, params):
        """ Constructor. """
        super(NoOut, self).__init__()
        self.name("NoOut")
        self.version("1.0")

    def output(self, data, params):
        """ Do nothing. """
        return data