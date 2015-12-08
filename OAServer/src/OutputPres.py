# -*- coding: utf-8 -*-
"""
Online Analysis - Post-processing output classes

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

import math
import numpy as np
from OACommon.BaseObject import BaseObject
from OACommon.DataObj import Scalar
from OACommon.DataObj import Array
from OACommon.DataObj import Image
PyTango = None


class Export2Tango(BaseObject):

    """ Export presentation data to TANGO. """

    def __init__(self, params):
        super(Export2Tango, self).__init__()
        self.name("Export2Tango")
        self.version("1.0")

        # Conditionally import PyTango
        global PyTango
        import PyTango

        try:
            self.dev = PyTango.DeviceProxy(params['device'])

        except PyTango.DevFailed as e:
            for err in e:
                self.logger.error("[%s] %s (Origin: %s)", self.name(), err.desc, err.origin)
            self.dev = None

    def output(self, data, params):
        """ Export data to the configured TANGO device. """

        # If the device is not defined return
        if not self.dev:
            return False

        if type(data) is not dict:
            self.logger.error("[%s] Input data has wrong type '%s'.", self.name(), type(data))
            return False

        try:
            # Cycle over keys in input data
            for key in data:
                # Check type
                if not isinstance(data[key], (Scalar, Array, Image)):
                    self.logger.warning("[%s] Dataset '%s' has wrong data type '%s'. Ignoring.", self.name(), key, type(data[key]))
                    continue

                if data[key].value is None:
                    self.logger.warning("[%s] Dataset '%s' is empty. Ignoring.", self.name(), key)
                    continue

                if np.any(np.isinf(data[key].value)):
                    self.logger.warning("[%s] Dataset '%s' contains Inf values and cannot be stored.", self.name(), key)
                    continue

                if np.any(np.isnan(data[key].value)):
                    self.logger.warning("[%s] Dataset '%s' contains NaN values and cannot be stored.", self.name(), key)
                    continue

                if not self._check_attr(key, data[key]):
                    # Need to recreate the attribute
                    if not self._create_attr(key, data[key]):
                        self.logger.error("[%s] '%s' attribute creation failed.", self.name(), key)
                        continue

                # Attribute is valid
                self._write_attr(str(key), data[key])

            return True

        except PyTango.DevFailed, e:
            self.logger.error("[%s] Error while updating TANGO attributes.", self.name())
            for err in e:
                self.logger.error("[%s] %s (Origin: %s)", self.name(), err.desc, err.origin)
                return False

    def reset(self, keys):
        """ Return reset flags for the given keys. """
        out = []
        for k in keys:
            try:
                f = self.dev.read_attribute(str(k) + "__reset").value
                if f:
                    self.logger.debug("[%s] Dataset '%s' has reset flag set. Resetting.", self.name(), k)
                    self.dev.write_attribute(str(k) + "__reset", False)
                out.append(f)
            except PyTango.DevFailed:
                self.logger.debug("[%s] Output '%s' has no reset attribute.", self.name(), k)
                out.append(False)
        return out

    def _write_attr(self, key, data):
        """ Internal. Write the main attribute and all the connected ones. """
        try:
            # Write main attribute
            self.dev.write_attribute(key, data.value)

            # Write bunches
            if hasattr(data, 'bunches') and data.bunches is not None and len(data.bunches) > 0:
                self.dev.write_attribute(key + "__bunches", data.bunches)

            # Write X axis
            if hasattr(data, '_x') and data._x is not None and len(data._x) > 0:
                self.dev.write_attribute(key + "__x", data._x)

        except PyTango.DevFailed, e:
            for err in e:
                self.logger.error("[%s] %s (Origin: %s)", self.name(), err.desc, err.origin)

    def _check_attr(self, key, data):
        """ Internal. Check existence of an attribute. """
        try:
            conf = self.dev.get_attribute_config(str(key))

            # Check source data type
            dtype = self._type2str(data.value.dtype)
            if dtype == False:
                return False

            # Check attribute data type
            if dtype != self._type2str(conf.data_type):
                return False

            # Check data format
            if isinstance(data, Scalar):
                if conf.data_format != PyTango.AttrDataFormat.SCALAR:
                    return False
                elif len(data.value.shape) > 1:
                    return False
                elif len(data.value.shape) == 1 and data.value.shape[0] != 1:
                    return False

            if isinstance(data, Array):
                if conf.data_format != PyTango.AttrDataFormat.SPECTRUM:
                    return False
                elif len(data.value.shape) != 1:
                    return False
                elif data.value.shape[0] > conf.max_dim_x:
                    return False

            if isinstance(data, Image):
                if conf.data_format != PyTango.AttrDataFormat.IMAGE:
                    return False
                elif len(data.value.shape) != 2:
                    return False
                elif data.value.shape[1] > conf.max_dim_x or data.value.shape[0] > conf.max_dim_y:
                    return False

            # Check __bunches (if needed)
            try:
                if data.bunches is not None and len(data.bunches) > 0:
                    conf = self.dev.get_attribute_config(str(key) + "__bunches")

                    # Check type
                    if conf.data_format != PyTango.AttrDataFormat.SPECTRUM:
                        return False

                    # Check size
                    if conf.max_dim_x < len(data.bunches):
                        return False

            except AttributeError:
                pass

            # Check __x
            try:
                if data._x is not None and len(data._x) > 0:
                    conf = self.dev.get_attribute_config(str(key) + "__x")

                    # Check size
                    if conf.max_dim_x < len(data.x):
                        return False
            except AttributeError:
                pass

            # Otherwise...
            return True

        except PyTango.DevFailed:
            # Attribute does not exist
            return False

    def _create_attr(self, key, data):
        """ Internal. Create a new attribute. """
        # First try to remove existing attribute with the same name.
        try:
            self.dev.command_inout('DeleteAttribute', str(key))
            self.dev.command_inout('DeleteAttribute', str(key) + "__x")
            self.dev.command_inout('DeleteAttribute', str(key) + "__bunches")
            self.dev.command_inout('DeleteAttribute', str(key) + "__reset")
        except PyTango.DevFailed, e:
            self.logger.error("[%s] Error deleting attributes (Error: %s)", self.name(), e[0].desc)

        # Then create the new attribute
        try:
            # Data type
            dtype = self._type2str(data.value.dtype)
            if dtype == False:
                self.logger.error("[%s] Cannot create attribute '%s'. Data has wrong type (%s).", self.name(), key, data.value.dtype)
                return False

            if isinstance(data, Scalar):
                # Scalar
                self.dev.NewScalar([str(key), dtype])

            elif isinstance(data, Array):
                # Spectrum
                self.dev.NewSpectrum([str(key), dtype, str(data.value.shape[0])])

            elif isinstance(data, Image):
                # Image
                self.dev.NewImage([str(key), dtype, str(data.value.shape[1]), str(data.value.shape[0])])

            else:
                # Unexpected type
                # NOTE: this point should be never reached as the type is checked before!
                raise Exception("Unexpected type '%s'" % type(data))

            # Create bunches array (if needed...)
            if hasattr(data, 'bunches') and data.bunches is not None and len(data.bunches) > 0:
                self.logger.debug("[%s] Dataset '%s' has bunches array of length %d.", self.name(), key, len(data.bunches))
                self.dev.NewSpectrum([str(key) + "__bunches", "ULONG", str(int(math.ceil(len(data.bunches) / 200.0) * 200))])

            # Create X array (if needed...)
            if hasattr(data, '_x') and data._x is not None and len(data._x) > 0:
                self.logger.debug("[%s] Dataset '%s' has an x axis of length %d.", self.name(), key, len(data._x))
                # Data type
                dtype = self._type2str(data._x.dtype)
                if dtype is not False:
                    self.dev.NewSpectrum([str(key) + "__x", dtype, str(len(data._x))])
                else:
                    self.logger.error("[%s] Cannot create attribute '%s__x'. Data has wrong type (%s).", self.name(), key, data.value.dtype)
                    return False

            # Create reset attribute
            self.dev.NewScalar([str(key) + "__reset", "BOOL"])
            self.dev.write_attribute(str(key) + "__reset", False)

        except PyTango.DevFailed, e:
            for err in e:
                self.logger.error("[%s] %s (Origin: %s)", self.name(), err.desc, err.origin)
            return False

        except Exception, e:
            self.logger.error("[%s] Error creating attribute '%s' (Error: %s)", self.name(), key, e, exc_info=True)
            return False

        else:
            return True

    def _type2str(self, data_type):
        if data_type == np.bool or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevBoolean):
            return "BOOL"
        elif data_type == np.uint8 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevUChar):
            return "UCHAR"
        elif data_type == np.uint16 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevUShort):
            return "USHORT"
        elif data_type == np.uint32 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevULong):
            return "ULONG"
        elif data_type == np.uint64 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevULong64):
            return "ULONG64"
        elif data_type == np.int16 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevShort):
            return "SHORT"
        elif data_type == np.int32 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevLong):
            return "LONG"
        elif data_type == np.int64 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevLong64):
            return "LONG64"
        elif data_type == np.float32 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevFloat):
            return "FLOAT"
        elif data_type == np.float64 or (type(data_type) != np.dtype and data_type == PyTango.ArgType.DevDouble):
            return "DOUBLE"
        else:
            return False


class NoOut(BaseObject):

    """ No-op presenter output handler. """

    def __init__(self, params):
        """ No-op constructor. """
        super(NoOut, self).__init__()
        self.name("NoOut")
        self.version("1.0")

    def output(self, data, params):
        """ No-op output function. Always return true. """
        self.logger.debug("[%s] Presenter output function called.", self.name())
        return True

    def reset(self, keys):
        """ No-op reset function. Always return false. """
        self.logger.debug("[%s] Presenter reset function called.", self.name())
        return [False for k in keys]