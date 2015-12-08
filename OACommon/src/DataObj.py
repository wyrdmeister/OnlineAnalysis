# -*- coding: utf-8 -*-
"""
Online Analysis - Classes to represent datasets

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

import numpy as np
from BaseObject import BaseObject


class BaseDataset(BaseObject):

    """ Base dataset class. """

    def __init__(self):
        """ Constructor. """
        super(BaseDataset, self).__init__()
        self.version("1.0")
        self.classtype("Raw")
        self.value = None
        self.attrs = {}

    def load(self, data, attrs={}):
        """ Initialize the object loading data from an HDF5 dataset. """
        self._check_data(data)
        if type(data) is np.ndarray:
            self.value = data
        elif type(data) is float:
            self.value = np.float64(data)
        elif type(data) in (int, long):
            self.value = np.int64(data)
        elif type(data) in (str, unicode):
            self.value = data
        elif type(data) in (np.float64, np.float32, np.int64, np.uint64, np.int32, np.uint32, np.int16, np.uint16, np.int8, np.uint8):
            self.value = data
        else:
            self.logger.warning("[%s] Dataset has unexpected type '%s'.", self.name(), type(data))
            self.data = data

        self.attrs = attrs

    def _check_data(self, data):
        """ Default data checker. Does nothing. """
        pass


class Scalar(BaseDataset):

    """ Hold a scalar dataset. """

    def __init__(self):
        """ Constructor. """
        super(Scalar, self).__init__()
        self.name("Scalar")

    def _check_data(self, data):
        """ Check that the scalar dataset is a 1D array (one for each shot)
        """
        if len(data.shape) != 1 or data.shape[0] < 2:
            raise Exception("Wrong data size %s" % data.shape)


class Array(BaseDataset):

    """ Hold an array dataset. """

    def __init__(self):
        """ Constructor. """
        super(Array, self).__init__()
        self.name('Array')

    def _check_data(self, data):
        """ Check that the array dataset is a 2D array (one array for each
        shot) and that is a numpy array
        """
        if type(data) != np.ndarray:
            raise Exception("Wrong data type '%s'" % type(data))
        if len(data.shape) != 2:
            raise Exception("Wrong data size %s" % data.shape)


class Image(BaseDataset):

    """ Hold an image dataset. """

    def __init__(self):
        """ Constructor. """
        super(Image, self).__init__()
        self.name('Image')

    def _check_data(self, data):
        """ Check that the array dataset is a 3D array (one array for each
        shot) and that is a numpy array
        """
        if type(data) != np.ndarray:
            raise Exception("Wrong data type '%s'" % type(data))
        if len(data.shape) != 3:
            raise Exception("Wrong data size %s" % data.shape)


class Metadata(BaseDataset):

    """ Hold an metadata dataset. """

    def __init__(self):
        """ Constructor. """
        super(Metadata, self).__init__()
        self.name('Metadata')

    def _check_data(self, data):
        """ No check... may be everything... """
        pass