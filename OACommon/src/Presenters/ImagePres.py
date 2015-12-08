# -*- coding: utf-8 -*-
"""
Online Analysis - Image presentations classes

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
from ..DataObj import Image


class ImageSum(BasePresentation):

    """ Can sum up images, average them giving a real average or can use a
    running average.
    """

    def __init__(self, params, filters):
        """ Constructor. """
        super(ImageSum, self).__init__(params, filters)
        self.name("ImageSum")
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
            self.logger.error("[%s] Error evaluating parameters. Algorithm will sum up images (Error: %s)", self.name(), e)
            self.params['mode'] = 'sum'
            self.params['alpha'] = 0.0

        if 'avg' in self.params:
            del self.params['avg']

    def reset(self, flags):
        """ Reset presenter. """
        self.image = None
        self.counter = 0

    def update(self, _f, target, **kwargs):
        """ Update the summed image. """
        # Get output name
        oname = self.outvars['output']

        # Create output image if it does not exist
        if self.output is None:
            self.output = {}
            self.output[oname] = Image()

        if self.image is None or self.image.shape != target.value.shape[1:]:
            # Empty output or size does not match. Reset image.
            self.image = np.zeros(target.value.shape[1:], dtype=np.float32)
            self.counter = 0

        if self.params['mode'] == 'runavg':
            # Running average: out = old * alpha + new * (1 - alpha)
            for i in range(target.value.shape[0]):
                if _f[i]:
                    self.image[:] = self.image[:] * self.params['alpha'] + target.value[i] * (1 - self.params['alpha'])
                    self.counter += 1
            self.output[oname].value = self.image

        else:
            # Normal average. Sum up the images and store in output the image divided by the counter
            self.image[:] += np.sum(target.value[_f], axis=0, dtype=np.float32)
            self.counter += np.sum(_f)

            if self.params['mode'] == 'avg':
                self.output[oname].value = self.image / self.counter

            else:
                self.output[oname].value = self.image

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

        # Weight for the running average
        delegates['avg'] = {
            'mandatory': True,  # Only for running average... but you can just put a zero for other modes!
            'type': 'expr',
            'dtype': 'int',
            'default': 0,
            'label': 'Averages',
            'delegate': None
        }

        return delegates


class ImageBackground(BasePresentation):

    """ ... """

    def __init__(self, params, filters):
        """ Constructor. """
        super(ImageBackground, self).__init__(params, filters)

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
            self.logger.error("[%s] Error evaluating parameters. Algorithm will sum up images (Error: %s)", self.name(), e)
            self.params['mode'] = 'avg'
            self.params['alpha'] = 0.0

        # Delete avg param (presenter should use alpha)
        if 'avg' in self.params:
            del self.params['avg']

    def reset(self, flags):
        """ Reset presenter. """
        self.img_counter = 0
        self.bkg_counter = 0
        self.image = None
        self.background = None

    def update(self, _f, target, period, bunches, **kwargs):
        """ Update presenter. """
        # Get output name
        oname = self.outvars['output']

        # Get signal and backgroun images
        _on = np.logical_and(_f, np.mod(bunches.value, period.value) != 0)
        _off = np.logical_and(_f, np.mod(bunches.value, period.value) == 0)

        # Create output image if it does not exist
        if self.output is None:
            self.output = {}
            self.output[oname] = Image()

        if self.image is None or self.image.shape != target.value.shape[1:]:
            # Empty output or size does not match. Reset image.
            self.image = np.zeros(target.value.shape[1:], dtype=np.float32)
            self.background = np.copy(self.image)
            self.img_counter = 0
            self.bkg_counter = 0

        if self.params['mode'] == 'runavg':
            # Running average: out = old * alpha + new * (1 - alpha)
            for i in range(target.value.shape[0]):
                if _on[i]:
                    self.image[:] = self.image[:] * self.params['alpha'] + target.value[i] * (1 - self.params['alpha'])
                    self.img_counter += 1
                elif _off[i]:
                    self.background[:] = self.background[:] * self.params['alpha'] + target.value[i] * (1 - self.params['alpha'])
                    self.bkg_counter += 1
            self.output[oname].value = self.image - self.background

        else:
            # Normal average. Sum up the images and store in output the image divided by the counter
            self.image[:] += np.sum(target.value[_on], axis=0, dtype=np.float32)
            self.img_counter += np.sum(_on)
            self.background[:] += np.sum(target.value[_off], axis=0, dtype=np.float32)
            self.bkg_counter += np.sum(_off)
            self.output[oname].value = self.image / self.img_counter - self.background / self.bkg_counter

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

        # Weight for the running average
        delegates['avg'] = {
            'mandatory': True,  # Only for running average... but you can just put a zero for other modes!
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