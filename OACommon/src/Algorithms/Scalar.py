# -*- coding: utf-8 -*-
"""
Online Analysis - Scalar manipulation algorithms

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
from ..DataObj import Metadata
import numpy as np


class ComputeScalarExpr(BaseAlgorithm):

    """ ComputeScalarExpr

    Compute an arbitrary scalar expression passed through the parameter
    'expression' that must correctly evaluate as a python expression.

    NOTE: both input and output variables should be scalars.

    """

    def __init__(self, params):
        """ Constructor. Initialize the processing lambda function. """
        super(ComputeScalarExpr, self).__init__(params)
        self.name("ComputeScalarExpr")
        self.version("1.0")

        try:
            # Get target variables
            if 'target' in self.invars:
                if type(self.invars['target']) is str:
                    t = [self.invars['target']]
                else:
                    t = self.invars['target']

                # Build a lambda function from 'target' variables and 'expression'
                self.function = eval("lambda %s: %s" % (', '.join(t), self.params['expression']), {"__builtins__": None, "np": np}, {})

                # Build wrapper lambda function
                self.wrapper = eval("lambda args: function(%s)" % (', '.join(["args[%d]" % i for i in range(len(t))])), {"__builtins__": None, "function": self.function}, {})

            else:
                self.wrapper = lambda args: np.float64(0)

        except Exception, e:
            self.logger.error("[%s]: cannot initialize expression variables (Error: %s)", self.name(), e)
            self.wrapper = lambda args: np.float64(0)

    def process(self, target, **kwargs):
        """ Assemble parameters and evaluate the lambda function. """
        # Find out output type
        if type(target) is dict:
            # Find output dimension
            n = 0
            for k in target:
                if type(target[k]) is Metadata:
                    continue
                elif n == 0:
                    n = target[k].value.shape[0]
                elif target[k].value.shape[0] != n:
                    self.logger.error("[%s] target variables have different dimension (%d != %d).", self.name(), target[k].value.shape[0], n)
                    return

            if n > 0:
                # Standard expression
                # Preallocation
                out = Scalar()
                out.value = np.zeros(shape=(n, ), dtype=np.float64)
                # Cycle over shots
                for i in range(n):
                    args = []
                    for k in target:
                        if type(target) is not Metadata:
                            args.append(np.float64(target[k].value[i]))
                        else:
                            args.append(np.float64(target[k].value))
                    out.value[i] = self.wrapper(args)

            else:
                # Metadata expression
                args = []
                for k in target:
                    args.append(np.float64(target[k].value))
                out = Metadata()
                out.value = np.float64(self.warpper(args))

        else:
            # Single target variable
            if type(target) is not Metadata:
                # Normal expression
                n = target.value.shape[0]
                out = Scalar()
                out.value = np.zeros(shape=(n, ), dtype=np.float64)
                # Cycle over all shots
                for i in range(n):
                    out.value[i] = self.wrapper([np.float64(target.value[i]), ])

            else:
                # Metadata expression
                out = Metadata()
                out.value = self.wrapper([np.float64(target.value), ])

        return {'output': out}

    @staticmethod
    def configure():
        """ Return parameters configuration. """

        delegates = {}

        # Expression to be evaluated
        delegates['expression'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'str',
            'label': 'Expression',
            'delegate': None
        }

        # List of target variables
        delegates['target'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'list>str',
            'label': 'Target',
            'delegate': None
        }

        return delegates


#class ComputeMetadataExpr(BaseAlgorithm):
#
#    """ ComputeMetadataExpr
#
#    Compute an arbitrary expression passed through the parameter
#    'expression' that works of the entire dataset from the file and return a
#    single scalar value that is then treated as a metadata value.
#
#    """
#
#    def __init__(self, params):
#        """ Constructor. Initialize the processing lambda function. """
#        super(ComputeMetadataExpr, self).__init__(params)
#        self.name("ComputeMetadataExpr")
#        self.version("1.0")
#
#        try:
#            # Get target variables
#            if 'target' in self.invars:
#                if type(self.invars['target']) is str:
#                    t = [self.invars['target']]
#                else:
#                    t = self.invars['target']
#
#                # Build a lambda function from 'target' variables and 'expression'
#                self.function = eval("lambda %s: %s" % (', '.join(t), self.params['expression']), {"__builtins__": None, "np": np}, {})
#
#                # Build wrapper lambda function
#                self.wrapper = eval("lambda args: function(%s)" % (', '.join(["args[%d]" % i for i in range(len(t))])), {"__builtins__": None, "function": self.function}, {})
#
#            else:
#                self.wrapper = lambda args: np.float64(0)
#
#        except Exception, e:
#            self.logger.error("[%s]: cannot initialize expression variables (Error: %s)", self.name(), e)
#            self.wrapper = lambda args: np.float64(0)
#
#    def process(self, target, **kwargs):
#        """ Assemble parameters and evaluate the lambda function. """
#        # Find out output type
#        if type(target) is dict:
#
#            args = []
#            for k in target:
#                args.append(target[k].value)
#
#            val = self.wrapper(args)
#
#        else:
#            val = self.wrapper(target.value)
#
#        # Check type of returned value
#        if type(val) in (int, long, float) or (hasattr(val, 'shape') and len(val.shape) == 0):
#            out = Metadata()
#            out.value = val
#            return {'output': out}
#
#        else:
#            self.logger.error("[%s] Metadata expression evaluated to an object that is not scalar.")
#            return {'output': None}