# -*- coding: utf-8 -*-
"""
Online Analysis - Scalar presentations classes

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

import inspect
import numpy as np

from BasePresentation import BasePresentation
from ..DataObj import Scalar
from ..DataObj import Array


class ScalarTrend(BasePresentation):

    """ Store and present the trend of a scalar value
    """

    def __init__(self, parameters, filters):
        """ Constructor. """
        super(ScalarTrend, self).__init__(parameters, filters)
        self.name("ScalarTrend")
        self.version("1.0")

        # Init variables
        self.reset([])

        # Check parameters
        try:
            s = int(eval(self.params['size'], {"__builtins__": None}, {}))
            if s > 0:
                self.params['size'] = s
            else:
                self.params['size'] = 500
        except Exception, e:
            self.logger.error("[%s] Cannot evaluate the size parameter. Setting size to 500. (Error: %s)", self.name(), e)
            self.params['size'] = 500

    def reset(self, flags):
        """ Reset presenter. """
        self.index = 0

    def update(self, _f, target, **kwargs):
        """ Update presenter. """
        # Get output name
        oname = self.outvars['output']

        if type(target) is not Scalar:
            self.logger.warning("[%s] Source variable type is not Scalar (%s).", self.name(), type(target))
            return

        if self.output is None:
            self.output = {}
            self.output[oname] = Array()
            self.output[oname].value = np.zeros((self.params['size'], ), dtype=target.value.dtype)
            self.index = 0

        # Number of values to insert
        n = np.sum(_f)
        self.logger.debug("[%s] Adding %d values to presenter.", self.name(), n)

        if self.params['size'] - self.index >= n:
            # Array not filled yet
            self.output[oname].value[self.index:(self.index + n)] = target.value[_f]
            self.index += n

        elif self.params['size'] == self.index:
            # Shift by n
            self.output[oname].value[0:-n] = self.output[oname].value[n:]
            # Set the value as the last n elements
            self.output[oname].value[-n:] = target.value[_f]

        else:
            # Shift by m = n - (size - index)
            m = n - (self.params['size'] - self.index)
            self.output[oname].value[0:-m] = self.output[oname].value[m:]
            # Set the value as the last n elements
            self.output[oname].value[-n:] = target.value[_f]
            # Set index equal to size
            self.index = self.params['size']

    @staticmethod
    def configure():
        """ Custom parameters configuration. """
        delegates = {}

        # Size
        delegates['size'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'int',
            'default': 1000,
            'label': 'Size',
            'delegate': None
        }

        return delegates


class ScalarHistogram(BasePresentation):

    """ Create a histogram of a scalar value
    """

    def __init__(self, parameters, filters):
        """ Constructor. """
        super(ScalarHistogram, self).__init__(parameters, filters)
        self.name("ScalarHistogram")
        self.version("1.0")

        # Init variables
        self.reset([])

        # Check parameters
        try:
            lim = eval(self.params['range'], {"__builtins__": None}, {})
            nbins = eval(self.params['bins'], {"__builtins__": None}, {})
            self.params['bins'] = np.linspace(lim[0], lim[1], nbins + 1)

        except Exception, e:
            self.logger.error("[%s] Failed to parse range and bins (Error: %s)", self.name(), e)
            self.params['bins'] = None

    def update(self, _f, target, **kwargs):
        """ Update presenter. """
        # Get output name
        oname = self.outvars['output']

        if self.params['bins'] is not None:
            h = np.histogram(target.value[_f], self.params['bins'])
            if self.output is None:
                self.output = {}
                self.output[oname] = Array()
                self.output[oname].value = np.int32(h[0])
                self.output[oname]._x = np.mean(np.vstack((h[1][0:-1], h[1][1:])), axis=0)
            else:
                self.output[oname].value += np.int32(h[0])

    @staticmethod
    def configure():
        """ Custom parameters configuration. """
        delegates = {}

        # Mode
        delegates['bins'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'int',
            'default': 100,
            'label': 'Number of bins',
            'delegate': None
        }

        delegates['range'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'list>num',
            'label': 'Range',
            'delegate': {
                'type': 'RangeInputDelegate',
                'm': 1,
            }
        }

        return delegates


class ScalarStatistics(BasePresentation):

    """ Keep history of a scalar value and present statistics about it.
    """

    def __init__(self, params, filters):
        """ Constructor. """
        super(ScalarStatistics, self).__init__(params, filters)
        self.name("ScalarStatistics")
        self.version("1.0")

        # Init variables
        self.reset([])

        # Stat functions
        func = ["mean", "std", "median"]

        # Check parameters
        try:
            self.params['out'] = []
            self.params['func'] = []

            if self.params['prefix'] != "":
                for f in func:
                    self.params['out'].append(self.params['prefix'] + "_" + f)
                    self.params['func'].append(getattr(np, f))

        except Exception, e:
            self.logger.error("[%s] Error initializing presenter (Error: %s)", self.name(), e)

        # Add names to output so that reset could work
        self.outvars['out'] = [self.params['prefix'] + "_" + f for f in func]

    def reset(self, flags):
        """ Reset presenter. """
        self.history = None

    def update(self, _f, target, **kwargs):
        """ Update presenter. """
        if self.output is None:
            self.output = {}
            for i in range(len(self.params['out'])):
                self.output[self.params['out'][i]] = Scalar()
            self.history = np.ndarray(shape=(0,), dtype=target.value.dtype)

        # Update history
        self.history = np.append(self.history, target.value[_f])

        # Store stats
        for i in range(len(self.params['out'])):
            if 'dtype' in inspect.getargspec(self.params['func'][i]).args:
                self.output[self.params['out'][i]].value = self.params['func'][i](self.history, dtype=np.float64)
            else:
                self.output[self.params['out'][i]].value = self.params['func'][i](self.history)

    @staticmethod
    def configure():
        """ Custom parameters configuration. """
        delegates = {}

        # Mode
        delegates['prefix'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'str',
            'label': 'Prefix',
            'delegate': None
        }

        delegates['output'] = None

        return delegates


class Scatter(BasePresentation):

    """ Build up data for a scatter plot. """

    def __init__(self, params, filters):
        """ Constructor. """
        super(Scatter, self).__init__(params, filters)
        self.name("Scatter")

    def update(self, _f, x, y, **kwargs):
        """ Update presenter. """
        # Get output name
        oname = self.outvars['output']

        if x.name() not in ("Scalar", "Metadata"):
            self.logger.error("[%s] X variable should be of type Scalar or Metadata. Found '%s'.", self.name(), x.name())
            return

        if y.name() not in ("Scalar", "Metadata"):
            self.logger.error("[%s] Y variable should be of type Scalar or Metadata. Found '%s'.", self.name(), y.name())
            return

        # Create output
        if self.output is None:
            self.output = {}
            self.output[oname] = Array()
            self.output[oname]._x = np.zeros(shape=(0,), dtype=x.value.dtype)
            self.output[oname].value = np.zeros(shape=(0,), dtype=y.value.dtype)

        # Apped data
        if x.name() == "Metadata" and y.name() == "Metadata":
            # Scatter plot of metadata values
            self.output[oname]._x = np.append(self.output[oname]._x, x.value)
            self.output[oname].value = np.append(self.output[oname].value, y.value)

        elif x.name() == "Metadata" and y.name() != "Metadata":
            self.output[oname]._x = np.append(self.output[oname]._x, np.tile(x.value, np.sum(_f)))
            self.output[oname].value = np.append(self.output[oname].value, y.value[_f])

        elif x.name() != "Metadata" and y.name() == "Metadata":
            self.output[oname]._x = np.append(self.output[oname]._x, x.value[_f])
            self.output[oname].value = np.append(self.output[oname].value, np.tile(y.value, np.sum(_f)))

        else:
            self.output[oname]._x = np.append(self.output[oname]._x, x.value[_f])
            self.output[oname].value = np.append(self.output[oname].value, y.value[_f])

    @staticmethod
    def configure():
        """ Custom parameters configuration. """
        delegates = {}

        # Remove targetr
        delegates['target'] = None

        # X source
        delegates['x'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'str',
            'label': 'X',
            'delegate': None
        }

        # Y source
        delegates['y'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'str',
            'label': 'Y',
            'delegate': None
        }

        return delegates