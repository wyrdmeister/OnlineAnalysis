# -*- coding: utf-8 -*-
"""
Online Analysis- Presentation filters

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

from BaseObject import BaseObject
import numpy as np


class _Filter(object):

    """ Private class that implements all the supported operators. """

    def __init__(self):
        """ Constructor. """
        self.target = ''
        self.eval = lambda x: False
        self.value = None
        self.operator = 'and'

    def _lt(self, val):
        """ Compare for less than. """
        return val < self.value

    def _gt(self, val):
        """ Compare for more than. """
        return val > self.value

    def _le(self, val):
        """ Compare for less than or equal. """
        return val <= self.value

    def _ge(self, val):
        """ Compare for more than or equal. """
        return val >= self.value

    def _eq(self, val):
        """ Compare for equal to. """
        return val == self.value

    def _neq(self, val):
        """ Compare for not equal to. """
        return val != self.value

    def _expr(self, val):
        """ Run lambda function. """
        return self.value(val)

    @staticmethod
    def _and(a, b):
        """ Static boolean operator AND. """
        return np.logical_and(a, b)

    @staticmethod
    def _or(a, b):
        """ Static boolean operator OR. """
        return np.logical_or(a, b)

    @staticmethod
    def _xor(a, b):
        """ Static boolean operator XOR. """
        return np.logical_xor(a, b)

    @staticmethod
    def _nor(a, b):
        """ Static boolean operator NOR. """
        return np.logical_not(np.logical_or(a, b))

    @staticmethod
    def _nand(a, b):
        """ Static boolean operator NAND. """
        return np.logical_not(np.logical_and(a, b))


class Filter(BaseObject):

    """ Implement a filter. """

    def __init__(self, filters):
        """ Constructor. Expect a dict of parameters for the filter. """
        super(Filter, self).__init__()
        self.name("Filter")
        self.version("1.0")

        # Parse filters
        self.filters = []
        for f in filters:
            try:
                nf = _Filter()

                # Set target
                nf.target = f['target']

                # Set evaluation function
                try:
                    nf.eval = getattr(nf, '_' + f['type'])
                except:
                    self.logger.warning("[%s] Unrecognized filter function '%s'.", self.name(), f['type'])
                    nf.eval = nf._eq

                # Set value
                if f['type'] == 'expr':
                    nf.value = eval("lambda x: " + f['value'], {"__builtins__": None, "np": np}, {})
                    self.logger.debug("[%s] Adding filter by expression: %s", self.name(), f['value'])
                else:
                    nf.value = eval(f['value'], {"__builtins__": None}, {})

                # Set operator
                try:
                    nf.operator = getattr(nf, '_' + f['operator'])
                except:
                    self.logger.warning("[%s] Unrecognized filter operator '%s'.", self.name(), f['operator'])
                    nf.operator = nf._and
            except Exception, e:
                self.logger.error("[%s] Error initializing filter (Error: %s)", self.name(), e, exc_info=True)
            else:
                self.logger.debug("[%s] Filter: target = %s, function=%s, operator=%s, value=%s.", self.name(), nf.target, nf.eval.func_name, nf.operator.func_name, str(nf.value))
                self.filters.append(nf)

    def evaluate(self, data):
        """ Evaluate filter conditions. """
        retval = None
        for f in self.filters:
            try:
                # Ignore filter that have as target non scalar values
                if data[f.target].name() != 'Scalar':
                    self.logger.warning("[%s] Target that are not of Scalar type are not supported in filters.", self.name())
                    continue

                # If is the first filter, just store result ...
                if retval == None:
                    retval = f.eval(data[f.target].value)

                # ... otherwise apply the configured operator
                else:
                    retval = f.operator(retval, f.eval(data[f.target].value))

            except KeyError, k:
                self.logger.error("[%s] Cannot find data element '%s' (Error: %s)", self.name(), f.target, k, exc_info=True)
            except Exception as e:
                self.logger.error("[%s] Exception while evaluating filters (Error: %s)", self.name(), e, exc_info=True)

        return retval