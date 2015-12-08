# -*- coding: utf-8 -*-
"""
Online Analysis - Data duplication algorithms

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
from copy import deepcopy


class DataCopy(BaseAlgorithm):

    """ A simple dataset duplicator

    This algorithm accept a single input and a single output. And does not
    accept any parameter.

    """

    def __init__(self, params):
        """ Constructor. """
        super(DataCopy, self).__init__(params)
        self.name("DataCopy")
        self.version("1.0")

    def process(self, target, **kwargs):
        """ Duplicate target object through copy.deepcopy. """
        return {'output': deepcopy(target)}


class Preserve(BaseAlgorithm):

    """ Change the type of a dataset to preserve it from processing to
    post processing. Can be also used to generate an alias.
    """

    def __init__(self, params):
        """ Constructor. """
        super(Preserve, self).__init__(params)
        self.name("Preserve")
        self.version("1.0")

    def process(self, target, **kwargs):
        """ Change the restype of the target dataset. """
        return {'output': target}