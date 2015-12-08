# -*- coding: utf-8 -*-

""" Module implementing presentation classes
"""

from ..BaseObject import BaseObject
from ..DataObj import Metadata
import numpy as np


class BasePresentation(BaseObject):

    """ Base presentation class

    This class provides basic serivices for presenters like parameter
    storage, I/O variable list evaluation and bunch numbers storage.

    Classes derived form this one must implement at least three methods:

    1) __init__(params): the constructor should be reimplemented and should
       call at first the __init__(params) method of this class. Then it
       should set the name and version of the object.
       After this it can do any specific initialization of the presenter.

    2) update(...): the update function takes as parameter...

    3) reset(): this method will be called when a reset of the preseter is
       requested.

    """

    def __init__(self, params, filters):
        """ Constructor. """
        super(BasePresentation, self).__init__()
        self.name("BasePresentation")
        self.version("1.0")

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

            elif params[p]['type'] == 'tango':
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

            elif params[p]['type'] in ('expr', 'list'):
                # Store parameters of type expression
                self.params[p] = params[p]['value']

            else:
                self.logger.warning("[%s] Ignoring parameter '%s' of unexpected type '%s'.", self.name(), p, params[p]['type'])

        # Init output variable
        self.output = None

        # Store filters
        self.filters = filters

    def _update(self, data):
        """ Update wrapper. Handle all the common stuff. """

        try:
            # 1) Evaluate filters
            f = self.filters.evaluate(data)

            if f is not None and not np.any(f):
                self.logger.debug("[%s] Filter conditions not met.", self.name())
                return

            # 2) Assemble input data
            args = {}
            n = 0
            for v in self.invars:
                if type(self.invars[v]) is list:
                    args[v] = {}
                    for sv in self.invars[v]:
                        args[v][sv] = data[sv]
                        if type(data[sv]) is not Metadata:
                            if n == 0:
                                n = data[sv].value.shape[0]
                            elif n != data[sv].value.shape[0]:
                                # BAD!
                                self.logger.error("[%s] Input datasets have different number of shots! (%d != %d)", self.name(), n, data[sv].value.shape[0])
                                return
                else:
                    args[v] = data[self.invars[v]]
                    if type(data[self.invars[v]]) is not Metadata:
                        if n == 0:
                            n = data[self.invars[v]].value.shape[0]
                        elif n != data[self.invars[v]].value.shape[0]:
                            # BAD!
                            self.logger.error("[%s] Input datasets have different number of shots! (%d != %d)", self.name(), n, data[self.invars[v]].value.shape[0])
                            return

            # 3) Set filters if needed
            if f is None:
                f = np.ones((n, ), dtype=np.bool)

            # 4) Call update
            self.logger.debug("[%s] Updating presenter.", self.name())
            self.update(_f=f, **args)

            # 5) Append bunch numbers
            if 'bunches' in self.invars:
                self.logger.debug("[%s] Adding %s bunch numbers to output.", self.name(), data[self.invars['bunches']].value[f])

                for v in self.output:
                    if not hasattr(self.output[v], 'bunches'):
                        self.output[v].bunches = np.ndarray(shape=(0,), dtype=data[self.invars['bunches']].value.dtype)
                    self.output[v].bunches = np.append(self.output[v].bunches, data[self.invars['bunches']].value[f])

        except KeyError as k:
            self.logger.error("[%s] Key error in update (Error: %s)", self.name(), k)
        except Exception as e:
            self.logger.error("[%s] Exception during update (Error: %s)", self.name(), e, exc_info=True)

    def _reset(self, flags):
        """ Reset presenter. """
        if all(flags):
            self.output = None
        elif self.output is not None:
            tags = self.output_tag
            for o in tags:
                if flags[tags.index(o)] and o in self.output:
                    del self.output[o]

        # Run custom reset
        self.reset(flags)

    def update(self, _f, **kwargs):
        """ Default update function. Do nothing. """
        pass

    def reset(self, flags):
        """ Default reset function. Do nothing. """
        pass

    def output_tag(self):
        """ Return output flags. """
        out = []
        for v in self.outvars:
            if type(v) is list:
                out += self.outvars[v]
            else:
                out.append(self.outvars[v])
        return out

    @staticmethod
    def default_configure():
        """ Base configuration function.
        Add delegates for standard parameters. """
        delegates = {}

        # Result type parameter
        delegates['output'] = {
            'mandatory': True,
            'type': 'tango',
            'dtype': 'str',
            'label': 'Output',
            'delegate': None
        }

        # Default input delegate
        delegates['target'] = {
            'mandatory': True,
            'type': 'var',
            'dtype': 'str',
            'label': 'Target',
            'delegate': None
        }

        # Default bunches delegate
        delegates['bunches'] = {
            'mandatory': False,
            'type': 'var',
            'dtype': 'str',
            'label': 'Bunches',
            'delegate': None
        }
        return delegates