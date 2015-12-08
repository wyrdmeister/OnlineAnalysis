# -*- coding: utf-8 -*-
"""
Online Analysis- Presenter class (post-processing entry-point)

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

# SQLite benchmarking module
#import Benchmarking


class Presenter(BaseObject):

    """ Call all configured presenters. """

    def __init__(self, config):
        """ Constructor. """
        super(Presenter, self).__init__()
        self.name("Presenter")
        self.version("1.0")
        self._presenters = config.presenters

    #@Benchmarking.sqlite_profile
    def update(self, data):
        """ Update presenters. """
        out = {}
        if data:
            for pres in self._presenters:
                # Update presenters
                pres[1]._update(data)

                # Get presenter output
                if pres[1].output is not None:
                    out.update(pres[1].output)
                else:
                    self.logger.debug("[%s] Presenter '%s' has empty output.", self.name(), pres[0])

        return out

    def reset(self, f):
        """ Reset presenters. """
        for p in self._presenters:
            try:
                out_tags = filter(None, p[1].output_tag())
                flags = f(out_tags)
                if any(flags):
                    self.logger.debug("[%s] Resetting presenter '%s'.", self.name(), p[0])
                    p[1]._reset(flags)
            except Exception, e:
                self.logger.error("[%s] Error calling reset method of presenter '%s' (Error: %s)", self.name(), p[0], e)