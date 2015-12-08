# -*- coding: utf-8 -*-
"""
Online Analysis - Spectrum presentations classes

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

from BasePresentation import BasePresentation
from ..DataObj import Array


class SpectrumSum(BasePresentation):

    """ Can sum up or average spectra

    """

    def __init__(self, parameters, filters):
        """ __init__(): class constructor
        """
        super(SpectrumSum, self).__init__(parameters, filters)
        self.name("SpectrumSum")
        self.version("1.0")

        # Init variables
        self.reset([])

        # Check parameters
        try:
            if 'mode' not in self.params:
                raise Exception("missing 'mode' parameter")

            if self.params['mode'] == 'sum':
                # Sum mode
                self.params['alpha'] = 0.0

            elif self.params['mode'] == 'avg':
                # Avg mode
                self.params['alpha'] = 0.0

            elif self.params['mode'] == 'runavg':
                # Running average
                a = int(eval(self.params['avg'], {"__builtins__": None}, {}))
                if a > 0:
                    self.params['alpha'] = (a - 1) / a
                else:
                    raise Exception("wrong value for 'avg' parameter (%d)" % (a, ))

            else:
                raise Exception("unknown value for 'mode' parameter (%s)" % (self.params['mode'], ))

        except Exception, e:
            self.logger.error("[%s] Error evaluating parameters. Algorithm will sum up spectra (Error: %s)", self.name(), e)
            self.params['mode'] = 'sum'
            self.params['alpha'] = 0.0

        # Mass calibration
        if 'calibration' in self.params:
            try:
                v = eval(self.params['calibration'], {"__builtins__": None}, {})
                if type(v) is not list:
                    raise Exception("calibration parameter did not evaluate to a list")
                if len(v) == 0:
                    raise Exception("")
                if len(v) != 2:
                    raise Exception("calibration parameter should be a list of two values")
                if type(v[0]) not in (int, long, float) or type(v[1]) not in (int, long, float):
                    raise Exception("calibration values should be numbers")
                if v[1] <= 0:
                    raise Exception("Calibration factor should be greater than zero")

                self.logger.debug("[%s] Loaded TOF calibration: %s.", self.name(), v)
                self.params['calibration'] = v
            except Exception, e:
                if str(e) != "":
                    self.logger.warning("[%s] Error configuring TOF calibration (Error: %s)", self.name(), e)
                del self.params['calibration']

        # Delete avg param (presenter should use alpha)
        if 'avg' in self.params:
            del self.params['avg']

    def reset(self, flags):
        """ Reset presenter. """
        self.spectrum = None
        self.counter = 0

    def update(self, _f, target, **kwargs):
        """ Update the summed image. """
        # Get output name
        oname = self.outvars['output']

        # Create output Array if it does not exist
        if self.output is None:
            self.output = {}
            self.output[oname] = Array()

        if self.spectrum is None or self.spectrum.shape != target.value.shape[1:]:
            # Empty output or size does not match. Reset image.
            self.spectrum = np.zeros(target.value.shape[1:], dtype=np.float32)
            self.counter = 0

            # Create calibrated mass axis
            if 'calibration' in self.params and self.params['calibration'] is not None:
                t0 = np.float32(self.params['calibration'][0])
                tk = np.float32(self.params['calibration'][1])
                t = np.arange(target.value.shape[1], dtype=np.float32)
                self.output[oname]._x = np.sign(t - t0) * np.power((t - t0) / tk, 2)

        if self.params['mode'] == 'runavg':
            # Running average: out = old * alpha + new * (1 - alpha)
            for i in range(target.value.shape[0]):
                if _f[i]:
                    self.spectrum[:] = self.spectrum[:] * self.params['alpha'] + target.value[i] * (1 - self.params['alpha'])
                    self.counter += 1
            self.output[oname].value = self.spectrum

        else:
            # Normal average. Sum up the images and store in output the image divided by the counter
            self.spectrum[:] += np.sum(target.value[_f], axis=0, dtype=np.float32)
            self.counter += np.sum(_f)

            if self.params['mode'] == 'avg':
                self.output[oname].value = self.spectrum / self.counter

            else:
                self.output[oname].value = self.spectrum

    @staticmethod
    def configure():
        """ Custom parameters configuration. """
        delegates = {}

        # Mode
        delegates['mode'] = {
            'mandatory': True,
            'type': 'list',
            'dtype': 'str',
            'default': 'avg',
            'label': 'Mode',
            'delegate': {
                'type': 'ComboboxDelegate',
                'values': ['sum', 'avg', 'runavg'],
                'labels': ['Sum', 'Average', 'Running average']
            }
        }

        # Mass calibration
        delegates['calibration'] = {
            'mandatory': False,
            'type': 'list',
            'dtype': 'list>num',
            'label': 'Mass calibration',
            'delegate': {
                'type': 'MassCalibrationDelegate'
            }
        }

        # Number of averages
        delegates['avg'] = {
            'mandatory': True,  # Only for running average mode, but you can just put a zero for other modes.
            'type': 'expr',
            'dtype': 'int',
            'default': 0,
            'label': 'Averages',
            'delegate': None
        }

        return delegates


class SpectrumBackground(BasePresentation):

    """ ... """

    def __init__(self, params, filters):
        """ Constructor. """
        super(SpectrumBackground, self).__init__(params, filters)

        # Init variables
        self.reset([])

        # Check parameters
        if 'mode' not in self.params:
            self.logger.warning("[%s] Mode parameter missing. Using default 'avg' mode.", self.name())
            self.params['mode'] = 'avg'

        try:
            if self.params['mode'] == 'avg':
                # Average mode
                self.params['alpha'] = 0.0

            elif self.params['mode'] == 'runavg':
                # Running average
                a = int(eval(self.params['avg'], {"__builtins__": None}, {}))
                if a > 0:
                    self.params['alpha'] = (a - 1) / a
                else:
                    raise Exception("wrong value for 'avg' parameter (%d)" % (a, ))

            else:
                raise Exception("unknown value for 'mode' parameter (%s)" % (self.params['mode'], ))

        except Exception, e:
            self.logger.error("[%s] Error evaluating parameters. Algorithm will sum up spectra (Error: %s)", self.name(), e)
            self.params['mode'] = 'avg'
            self.params['alpha'] = 0.0

        # Delete avg param (presenter should use alpha)
        if 'avg' in self.params:
            del self.params['avg']

    def reset(self, flags):
        """ Reset presenter. """
        self.spectrum_counter = 0
        self.bkg_counter = 0
        self.spectrum = None
        self.background = None

    def update(self, _f, target, period, bunches, **kwargs):
        """ Update presenter. """
        # Get output name
        oname = self.outvars['output']

        # Get signal and backgroun images
        _on = np.logical_and(_f, np.mod(bunches.value, period.value) != 0)
        _off = np.logical_and(_f, np.mod(bunches.value, period.value) == 0)

        # Create output spectrum if it does not exist
        if self.output is None:
            self.output = {}
            self.output[oname] = Array()

        if self.spectrum is None or self.spectrum.shape != target.value.shape[1:]:
            # Empty output or size does not match. Reset spectrum.
            self.spectrum = np.zeros(target.value.shape[1:], dtype=np.float32)
            self.background = np.copy(self.spectrum)
            self.spectrum_counter = 0
            self.bkg_counter = 0

        if self.params['mode'] == 'runavg':
            # Running average: out = old * alpha + new * (1 - alpha)
            for i in range(target.value.shape[0]):
                if _on[i]:
                    self.spectrum[:] = self.spectrum[:] * self.params['alpha'] + target.value[i] * (1 - self.params['alpha'])
                    self.spectrum_counter += 1
                elif _off[i]:
                    self.background[:] = self.background[:] * self.params['alpha'] + target.value[i] * (1 - self.params['alpha'])
                    self.bkg_counter += 1
            self.output[oname].value = self.spectrum - self.background

        else:
            # Normal average. Sum up the images and store in output the spectrum divided by the counter
            self.spectrum[:] += np.sum(target.value[_on], axis=0, dtype=np.float32)
            self.spectrum_counter += np.sum(_on)
            self.background[:] += np.sum(target.value[_off], axis=0, dtype=np.float32)
            self.bkg_counter += np.sum(_off)
            self.output[oname].value = self.spectrum / self.spectrum_counter - self.background / self.bkg_counter

    @staticmethod
    def configure():
        """ Custom parameters configuration. """
        delegates = {}

        # Mode
        delegates['mode'] = {
            'mandatory': True,
            'type': 'list',
            'dtype': 'str',
            'default': 'avg',
            'label': 'Mode',
            'delegate': {
                'type': 'ComboboxDelegate',
                'values': ['avg', 'runavg'],
                'labels': ['Average', 'Running average']
            }
        }

        # Mass calibration
        delegates['calibration'] = {
            'mandatory': False,
            'type': 'list',
            'dtype': 'list>num',
            'label': 'Mass calibration',
            'delegate': {
                'type': 'MassCalibrationDelegate'
            }
        }

        # Number of averages
        delegates['avg'] = {
            'mandatory': True,  # Only for running average mode, but you can just put a zero for other modes.
            'type': 'expr',
            'dtype': 'int',
            'default': 0,
            'label': 'Averages',
            'delegate': None
        }

        # Background period
        delegates['period'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'str',
            'label': 'Background period',
            'delegate': None
        }

        # Override bunches configuration. For this presenter the parameter is mandatory!
        delegates['bunches'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'str',
            'label': 'Bunches',
            'delegate': None
        }

        return delegates