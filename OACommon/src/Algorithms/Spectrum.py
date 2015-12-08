# -*- coding: utf-8 -*-
"""
Online Analysis - Spectrum manipulation algorithms

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

from BaseAlgorithm import BaseAlgorithm
from ..DataObj import Scalar
from ..DataObj import Array
import numpy as np


class IntegratePeaks(BaseAlgorithm):

    """ Integrate spectrum slices.

    This algorithm integrate an arbitrary number of spectrum slices. It may
    be used to integrate peaks in a TOF spectrum.

    Parameters:
    - ranges: limits of the slices to integrate. This parameter must
      evaluate correctly as a list of lists. Each list should have two values
      defining the limits of one slice.
      NOTE: if the target variable is an array then values are interpreted as
      indexes and must be integers. If instead is a spectrum (an array with
      an X axis) then are compared with the actual values and they may be
      floats.

      Example: Array => [ [10, 20], [50, 60] ]
               Spectrum => [ [2.45, 3.5], [10.4, 12.5] ]

    - output: the number of variables should be 1 (the integrals are returned
      as an array) or one var for each slice.

    """

    def __init__(self, params):
        """ Constructor. Evaluate ranges and check output variables. """
        super(IntegratePeaks, self).__init__(params)
        self.name("IntegratePeaks")
        self.version("1.0")

        try:
            # Eval slices
            slices = eval(self.params['ranges'], {"__builtins__": None}, {})

            if type(slices) is not list:
                self.logger.error("[%s] Error while evaluating slice limits. (Error: var evaluated to wrong type '%s')", self.name(), type(slices))
                self.params['ranges'] = []

            else:
                if len(slices) == 2 and type(slices[0]) in (int, long, float) and type(slices[1]) in (int, long, float):
                    # Single slice
                    self.params['ranges'] = [slices]
                else:
                    for s in slices:
                        if type(s) is not list or len(s) != 2 or type(s[0]) not in (int, long, float) or type(s[1]) not in (int, long, float) or s[0] >= s[1]:
                            # Remove bad slices...
                            slices[slices.index(s)] = []
                    self.params['ranges'] = slices

            # Check that the number of slices are the same as the number of
            # output variables
            if type(self.outvars['output']) == list:
                n = len(self.outvars['output']) - len(self.params['ranges'])
                if n > 0:
                    # More outputs than slices. Add some empty ranges.
                    self.logger.warning("[%s] Adding %d empty ranges.", self.name(), n)
                    for i in range(n):
                        self.params['ranges'].append([])

                elif n < 0:
                    # More slices than outputs (or equal)
                    self.logger.warning("[%s] Removing %d ranges without an output variable.", self.name(), -n)
                    for i in range(-n):
                        self.params['ranges'].pop()

            # Eval baseline flag
            if 'baseline' in self.params and eval(self.params['baseline'], {"__builtins__": None}, {}) == 1:
                self.params['baseline'] = True
            else:
                self.params['baseline'] = False

        except Exception, e:
            self.logger.error("[%s] Error evaluating ranges (Error: %s)", self.name(), e)
            self.params['ranges'] = []

    def process(self, target, **kwargs):
        """ Integrate slices. """
        if type(target) is Array:
            # Output first dimension
            n = target.value.shape[0]

            # Compute slices integrals
            peaks = []
            for s in self.params['ranges']:
                if len(s) == 0:
                    peaks.append(np.zeros((n, )))
                    continue

                # Extend end of slice by one as numpy indexing does not include
                # the last element. [a:b] => [a, b)
                s[1] += 1

                if s[0] < 0 or s[0] >= target.value.shape[1]:
                    self.logger.warning("[%s] Bad range lower limit '%d'. Target shape was: %s.", self.name(), s[0], target.value.shape)
                    continue

                if s[1] < 0 or s[1] >= target.value.shape[1]:
                    self.logger.warning("[%s] Bad range upper limit '%d'. Target shape was: %s.", self.name(), s[1], target.value.shape)
                    continue

                # Compute baseline
                if self.params['baseline']:
                    # Base endpoints calculation
                    # Limits
                    delta = 10
                    br = [s[0] - delta / 2, s[0] + delta / 2]
                    er = [s[1] - delta / 2, s[1] + delta / 2]
                    # Check limits
                    if br[0] < 0:
                        br[0] = 0
                    if br[1] >= target.value.shape[1]:
                        br[1] = target.value.shape[0] - 1
                    if er[0] < 0:
                        er[0] = 0
                    if er[1] >= target.value.shape[1]:
                        er[1] = target.value.shape[1] - 1
                    if er[0] < br[1]:
                        # Skip
                        self.logger.warning("[%s] Bad baseline range. R: %s, BR: %s, ER: %s", self.name(), s, br, er)
                        continue

                    # Baseline start
                    start = np.mean(target.value[:, br[0]:br[1]], axis=1)
                    # Baseline stop
                    stop = np.mean(target.value[:, er[0]:er[1]], axis=1)
                    # Baseline matrix
                    x = np.arange(s[0], s[1]) - s[0]
                    baseline = np.tile((stop - start) / (s[1] - s[0]), (x.shape[0], 1)).T * np.tile(x, (n, 1)) + np.tile(start, (x.shape[0], 1)).T

                else:
                    baseline = 0

                peaks.append(np.sum(target.value[:, s[0]:s[1]] - baseline, dtype=np.float64, axis=1))

            # Store output
            if type(self.outvars['output']) is not list:
                out = Scalar()
                if len(peaks) > 0:
                    out.value = peaks[0]
                else:
                    out.value = np.zeros((n, ))
                return {'output': out}

            else:
                out = {}
                for k in self.outvars['output']:
                    out[k] = Scalar()
                    out[k].value = peaks[self.outvars['output'].index(k)]
                return out

        else:
            raise NotImplemented("Unsupported target type (%s)" % type(target))

    @staticmethod
    def configure():
        """ Return parameters configuration. """

        delegates = {}

        # Integration ranges
        delegates['ranges'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'list>list>int',
            'label': 'Ranges',
            'delegate': {
                'type': 'RangeInputDelegate',
                'm': None
            }
        }

        # Baseline subtraction flag
        delegates['baseline'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'bool',
            'label': 'Baseline',
            'default': 0,
            'delegate': {
                'type': 'CheckboxDelegate'
            }
        }

        # Output variable list
        delegates['output'] = {
            'mandatory': True,
            'type': 'outvar',
            'dtype': 'list>str',
            'label': 'Output',
            'delegate': None
        }

        return delegates


class DigitizerSplit(BaseAlgorithm):

    """ Split digitizer traces

    Split the digitizer traces that comes packed together in a single array.

    """

    def __init__(self, params):
        """ Constructor. """
        super(DigitizerSplit, self).__init__(params)
        self.name("DigitizerSplit")
        self.version("1.0")

        # Eval channel number
        try:
            ch = int(eval(self.params['channel'], {"__builtins__": None}, {}))
            if ch < 0 or ch > 7:
                self.params['channel'] = None
            else:
                self.params['channel'] = ch
        except Exception, e:
            self.logger.error("[%s] Error evaluating channel number (Error: %s)", self.name(), e)
            self.params['channel'] = None

        # Eval baseline subtraction
        if "baseline" in self.params:
            try:
                t = eval(self.params['baseline'], {"__builtins__": None}, {})
                if type(t) is not list:
                    raise Exception("baseline evaluated to wrong type")

                if len(t) == 2:
                    if type(t[0]) not in (int, long):
                        raise Exception("baseline indexes must be integers")
                    if type(t[1]) not in (int, long):
                        raise Exception("baseline indexes must be integers")
                    if t[0] >= t[1]:
                        raise Exception("baseline indexes should identify a valid range of points")
                    self.params['baseline'] = t

                else:
                    raise Exception("")

            except Exception, e:
                if str(e) != "":
                    self.logger.error("[%s] Error evaluating baseline parameter (Error: %s)", self.name(), e)
                del self.params['baseline']

    def process(self, target, **kwargs):
        """ Extract selected channel. """
        # Init output
        out = Array()

        # Check channel mask
        if 'ChannelMask' in target.attrs and 'ChannelSize' in target.attrs:
            if self.params['channel'] != None and target.attrs['ChannelMask'] & (2 ** self.params['channel']):
                count = 0
                dsize = int(target.attrs['ChannelSize'])
                val = target.attrs['ChannelMask'] & (2 ** self.params['channel'] - 1)
                while val:
                    val &= val - 1
                    count += 1

                val = np.copy(target.value[:, (count * dsize):((count + 1) * dsize - 1)])
                if 'baseline' in self.params:
                    baseline = np.mean(val[:, self.params['baseline'][0]:self.params['baseline'][1]], axis=1, dtype=np.float32)
                    val = np.float32(val) - np.tile(baseline, (val.shape[1], 1)).T

                out.value = val
                return {'output': out}

            else:
                # Missing channel
                self.logger.warning("[%s] Channel %d is not available.", self.name(), self.params['channel'])

        else:
            # Missing attributes
            self.logger.error("[%s] Missing dataset attribute. Cannot extract required channel.", self.name())

        # Set output to default empty array
        out.value = np.zeros(shape=(0, ), dtype=target.value.dtype)
        return {'output': out}

    @staticmethod
    def configure():
        """ Return parameters configuration. """

        delegates = {}

        # Channel
        delegates['channel'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'int',
            'label': 'Channel',
            'default': 0,
            'delegate': {
                'type': 'ComboboxDelegateID',
                'labels': ['Ch. 0', 'Ch. 1', 'Ch. 2', 'Ch. 3', 'Ch. 4', 'Ch. 5', 'Ch. 6', 'Ch. 7']
            }
        }

        # Baseline subtraction range
        delegates['baseline'] = {
            'mandatory': False,
            'type': 'expr',
            'dtype': 'list>int',
            'label': 'Baseline range',
            'delegate': {
                'type': 'RangeInputDelegate',
                'm': 1,
            }
        }

        return delegates


class DigitizerJitter(BaseAlgorithm):

    """ Compute the t0 of digitizer trigger based on a trigger signal. """

    def __init__(self, params):
        """ Constructor. """
        super(DigitizerJitter, self).__init__(params)

        # Check threshold parameter
        if 'fraction' in self.params:
            try:
                t = eval(self.params['fraction'], {"__builtins__": None}, {})

                if type(t) not in (float, ):
                    raise Exception("fraction evaluated to wrong type.")
                if t > 1.0:
                    raise Exception("fraction cannot be more than 1")
                if t < 0:
                    raise Exception("fraction cannot be negative")
                if t == 0:
                    raise Exception("")

                self.params['fraction'] = t

            except Exception, e:
                if str(e) != "":
                    self.logger.error("[%s] Error evaluating fraction parameter (Error: %s)", self.name(), e)
                del self.params['fraction']

        # Maximum t0
        if 'maxt0' in self.params:
            try:
                t = eval(self.params['maxt0'], {"__builtins__": None}, {})

                if type(t) not in (int, long):
                    raise Exception("maximum t0 evaluated to wrong type.")
                if t < 0:
                    raise Exception("maximum t0 cannot be negative")
                self.params['maxt0'] = t

            except Exception, e:
                self.logger.error("[%s] Error evaluating fraction parameter (Error: %s)", self.name(), e)
                self.params['maxt0'] = 0
        else:
            self.params['maxt0'] = 0

    def process(self, target, reference, **kwargs):
        """ Extract t0 for the digitizer from target channel. """
        if reference.name() != "Array":
            self.warning("[%s] Input variable must be of type Array. Found %s.", self.name(), type(target))
            return

        if 'fraction' in self.params:
            wl = 7
            w = np.ones(wl, dtype=np.float64)
            sp = np.hstack((reference.value[:, wl - 1:0:-1], reference.value, reference.value[:, -1:-wl:-1]))

            for i in np.arange(sp.shape[0]):
                c = np.convolve(w / w.sum(), sp[i], mode='valid')
                delta = (c.shape[0] - target.value.shape[0]) / 2
                c = c[delta:c.shape[0] - delta]

                th = self.params['fraction'] * np.max(c)
                t0 = np.sum(np.cumsum(c > th) == 0, dtype=np.int32) - 50

                if t0 > 0 and t0 < self.params['maxt0']:
                    target.value[i, 0:target.value.shape[1] - t0] = target.value[i, t0:]
                    target.value[target.value.shape[1] - t0:] = 0

        return {}

    @staticmethod
    def configure():
        """ Return parameters configuration. """

        delegates = {}

        # Reference waveform
        delegates['reference'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'str',
            'label': 'Reference',
            'delegate': None
        }

        # CFD fraction
        delegates['fraction'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'num',
            'default': 0.5,
            'label': 'Fraction',
            'delegate': None
        }

        # Max correction
        delegates['maxt0'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'int',
            'default': 200,
            'label': 'Max. T0',
            'delegate': None
        }

        # Remove output
        delegates['output'] = None

        return delegates