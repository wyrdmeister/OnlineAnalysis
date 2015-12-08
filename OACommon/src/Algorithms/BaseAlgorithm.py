# -*- coding: utf-8 -*-
"""
Online Analysis - Base algorithm class

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

from ..BaseObject import BaseObject


class BaseAlgorithm(BaseObject):

    """ Base algorithm class

    This class provides basic serivices like parameter storage, I/O variable
    list evaluation and result class settings.

    Classes derived form this one must implement at least two methods:

    1) __init__(params): the constructor should be reimplemented and should
       call at first the __init__(params) method of this class. Then it
       should call the methods name() and version().
       After this can be implmented any specific initialization of the
       algorithm.

    2) process(...): the process function takes ...

    """

    def __init__(self, params):
        """ Constructor. Do basic initializtion of the algorithm class. """

        # Call parent constructor
        super(BaseAlgorithm, self).__init__()
        # Setup name
        self.name("BaseAlgorithm")
        self.version("1.0")

        # Default result class
        self.resclass = "Partial"

        # Store parameters, splitting params from invars and outvars
        self.params = {}
        self.invars = {}
        self.outvars = {}

        for p in params:
            if params[p]['type'] == 'var':
                # Store input variables
                try:
                    t = eval(params[p]['value'], {"__builtins__": None}, {})
                    if type(t) in (str, unicode):
                        # Single string
                        self.invars[p] = t

                    elif type(t) is list and len(t) > 0:
                        # List of strings
                        for v in t:
                            if type(v) not in (str, unicode):
                                self.logger.error("[%s] The input variable '%s' evaluated incorrectly. A list of variables shoulb be a list of strings and not '%s'.", self.name(), p, type(v))
                                break
                        else:
                            # Add variable list
                            self.invars[p] = t
                    else:
                        # Unexpected type
                        self.logger.error("[%s] The input variable '%s' evaluated to an incorrect type '%s'.", self.name(), p, type(t))

                except NameError:
                    # Single variable
                    self.invars[p] = params[p]['value']

                except Exception, e:
                    # Error
                    self.logger.error("[%s] Error evaluating input variable '%s' (Error: %s)", self.name(), p, e)

            elif params[p]['type'] == 'outvar':
                # Store output variables
                try:
                    t = eval(params[p]['value'], {"__builtins__": None}, {})
                    if type(t) in (str, unicode):
                        # Single string
                        self.outvars[p] = t

                    elif type(t) is list and len(t) > 0:
                        # List of strings
                        for v in t:
                            if type(v) not in (str, unicode):
                                self.logger.error("[%s] The output variable '%s' evaluated incorrectly. A list of variables shoulb be a list of strings and not '%s'.", self.name(), p, type(v))
                                break
                        else:
                            # Add variable list
                            self.outvars[p] = t
                    else:
                        # Unexpected type
                        self.logger.error("[%s] The output variable '%s' evaluated to an incorrect type '%s'.", self.name(), p, type(t))

                except NameError:
                    # Single variable
                    self.outvars[p] = params[p]['value']

                except Exception, e:
                    # Error
                    self.logger.error("[%s] Error evaluating output variable '%s' (Error: %s)", self.name(), p, e)

            elif params[p]['type'] == 'restype':
                # Manage result type
                try:
                    val = eval(params[p]['value'], {"__builtins__": None}, {})
                    if val == 0:
                        self.resclass = "Raw"
                    elif val == 1:
                        self.resclass = "Result"
                except Exception, e:
                    self.logger.error("[%s] Error evaluating parameter '%s' of type 'restype' (Error: %s)", self.name(), p, e)

            elif params[p]['type'] in ('expr', 'list'):
                # Store parameters of type expression
                self.params[p] = params[p]['value']

            else:
                self.logger.warning("[%s] Ignoring parameter '%s' of unexpected type '%s'.", self.name(), p, params[p]['type'])

    def _process(self, data):
        """ Processing function wrapper called by the OA.

        This function should not be overridden. All the processing code
        should be implemented by the process() function.

        """
        try:
            # 1) Create input variables
            args = {}
            for v in self.invars:
                if type(self.invars[v]) is list:
                    args[v] = {}
                    for sv in self.invars[v]:
                        args[v][sv] = data[sv]
                else:
                    args[v] = data[self.invars[v]]

            # 2) Processing
            self.logger.debug("[%s] Running algorithm.", self.name())
            retval = self.process(**args)

            # 3) Store output variables
            for v in self.outvars:
                if type(self.outvars[v]) is list:
                    # List of outputs
                    for sv in self.outvars[v]:
                        try:
                            data[sv] = retval[sv]
                            data[sv].classtype(self.resclass)

                        except KeyError, k:
                            self.logger.error("[%s] Cannot find output variable '%s'.", self.name(), k)

                else:
                    # Single output
                    try:
                        data[self.outvars[v]] = retval[v]
                        data[self.outvars[v]].classtype(self.resclass)

                    except KeyError, k:
                        self.logger.error("[%s] Cannot find output variable %s.", self.name(), k)

        except KeyError, k:
            self.logger.error("[%s]: KeyError (%s)", self.name(), k, exc_info=True)
        except ValueError, v:
            self.logger.error("[%s]: ValueError (%s)", self.name(), v, exc_info=True)
        except Exception, e:
            self.logger.error("[%s]: Exception (%s)", self.name(), e, exc_info=True)

    def process(self):
        """ Processing function

        Should be overridden in all derived classes. In the base implementation
        it does nothing.

        """
        pass

    @staticmethod
    def default_configure():
        """ Base configuration function.
        Add delegates for standard parameters. """
        delegates = {}

        # Result type parameter
        delegates['result'] = {
            'mandatory': True,
            'type': 'restype',
            'dtype': 'int',
            'label': 'Result type',
            'default': 2,
            'delegate': {
                'type': 'ComboboxDelegateID',
                'labels': ['Raw', 'Result', 'Partial']
            }
        }

        # Default input delegate
        delegates['target'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'str',
            'label': 'Target',
            'delegate': None
        }

        # Default output delegate
        delegates['output'] = {
            'mandatory': True,
            'type': 'outvar',
            'dtype': 'str',
            'label': 'Output',
            'delegate': None
        }

        return delegates