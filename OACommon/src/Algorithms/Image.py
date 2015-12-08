# -*- coding: utf-8 -*-
"""
Online Analysis - Image manipulation algorithms

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
from ..DataObj import Image
from ..DataObj import Array
import numpy as np


class ImageFilter(BaseAlgorithm):

    """ A simple image filter.

    This algorithm can subtract a baseline from the image and then apply a
    threshold, setting as zero all pixles below the configured level.

    Parameters:
    - baseline: baseline level. Should be of the same type as the image
      (usually uint16).
    - threshold: threshold level

    Both parameters should evaluate correcty as numbers (int, long, float).

    """
    def __init__(self, params):
        """ Constructor. Evaluate baseline and threshold values. """
        super(ImageFilter, self).__init__(params)
        self.name("ImageFilter")
        self.version("1.0")

        # Check parameters
        if 'baseline' in self.params:
            try:
                self.params['baseline'] = eval(self.params['baseline'], {"__builtins__": None}, {})
                if not isinstance(self.params['baseline'], (int, long, float)):
                    raise Exception("wrong type [%s]" % type(self.params['baseline']))

            except Exception, e:
                self.logger.error("[%s] baseline parameter cannot be evaluated (Error: %s)", self.name(), e)
                del self.params['baseline']

        if 'threshold' in self.params:
            try:
                self.params['threshold'] = eval(self.params['threshold'], {"__builtins__": None}, {})
                if not isinstance(self.params['threshold'], (int, long, float)):
                    raise Exception("wrong type [%s]" % type(self.params['threshold']))

            except Exception, e:
                self.logger.error("[%s] threshold parameter cannot be evaluated (Error: %s)", self.name(), e)
                del self.params['threshold']

    def process(self, target, **kwargs):
        """ Filter the image.

        First the image is copied (with copy.deepcopy), then the baseline is
        subtracted (maintaining the numeric type of the image). All pixels
        with a value below the threshold are set to zero.

        """
        out = Image()
        out.value = np.copy(target.value)

        # Subtract baseline
        if 'baseline' in self.params:
            # Assure that we do not get negative numbers
            out.value[out.value < self.params['baseline']] = self.params['baseline']
            # Actually subtract baseline
            out.value[:] = out.value[:] - self.params['baseline']

        # Apply threshold
        if 'threshold' in self.params:
            out.value[out.value < self.params['threshold']] = 0

        return {'output': out}

    @staticmethod
    def configure():
        """ Return parameters configuration. """
        delegates = {}

        # Image baseline
        delegates['baseline'] = {
            'mandatory': False,
            'type': 'expr',
            'dtype': 'int',
            'default': 0,
            'label': 'Baseline',
            'delegate': None
        }

        # Filter threshold
        delegates['threshold'] = {
            'mandatory': False,
            'type': 'expr',
            'dtype': 'num',
            'default': 0.0,
            'label': 'Threshold',
            'delegate': None
        }

        return delegates


class ImageBin(BaseAlgorithm):

    """ A 2x2 binning algorithm. Does not accept any parameter. """

    def __init__(self, params):
        """ Constructor. """
        super(ImageBin, self).__init__(params)
        self.name("ImageBin")
        self.version("1.0")

    def process(self, target, **kwargs):
        """ Bin the target image 2x2. """
        # Check that target is an image
        if target.name() != 'Image':
            self.logger.error("[%s] Input variable is not an image. Skipping.", self.name())
            return {'output': None}

        out = Image()
        out.value = target.value[:, 0::2, 0::2] + target.value[:, 1::2, 0::2] + target.value[:, 1::2, 0::2] + target.value[:, 1::2, 0::2]
        return {'output': out}


class ImageProfile(BaseAlgorithm):

    """ Image integration.

    Compute a vertical and horizontal profile of the target image. An
    optional Area-Of-Interest (AOI) may be defined by the 'aoi' parameter.

    """

    def __init__(self, params):
        """ Constructor. Evaluate the AOI. """
        super(ImageProfile, self).__init__(params)
        self.name("ImageProfile")
        self.version("1.0")

        # Get AOI
        self.aoi = None
        if 'aoi' in self.params:
            try:
                self.aoi = eval(self.params['aoi'], {"__builtins__": None}, {})
                assert(type(self.aoi) is list)
                assert(len(self.aoi) == 4)
            except Exception, e:
                self.logger.error("[%s] Cannot evaluate 'aoi' definition. Ignoring (Error: %s)", self.name(), e)
                self.aoi = None

    def process(self, target, **kwargs):
        """ Compute the vertical and horizonal profiles. """
        # Get view
        if self.aoi:
            view = target.value[:, self.aoi[2]:self.aoi[3], self.aoi[0]:self.aoi[1]]
        else:
            view = target.value

        # Integrate output
        outh = Array()
        outh.value = np.sum(view, 1)
        outv = Array()
        outv.value = np.sum(view, 2)

        return {'out_hor': outh, 'out_vert': outv}

    @staticmethod
    def configure():
        """ Return parameters configuration. """
        delegates = {}

        # Optional area of interest
        delegates['aoi'] = {
            'mandatory': False,
            'type': 'expr',
            'dtype': 'list>int',
            'label': 'Area of Interest',
            'delegate': {
                'type': 'AOIDelegate',
            }
        }

        # Remove output delegate
        delegates['output'] = None

        # Horizontal profile output
        delegates['out_hor'] = {
            'mandatory': True,
            'type': 'outvar',
            'dtype': 'str',
            'label': 'H profile',
            'delegate': None
        }

        # Vertical profile output
        delegates['out_vert'] = {
            'mandatory': True,
            'type': 'outvar',
            'dtype': 'str',
            'label': 'V profile',
            'delegate': None
        }

        return delegates


class ImageAnnularFilter(BaseAlgorithm):

    """ Image annular filtering

    Select an annulus of a VMI image, setting at zero all the pixel outside
    the defined region

    """

    def __init__(self, params):
        """ Constructor. Evaluate the AOI. """
        super(ImageAnnularFilter, self).__init__(params)
        self.name("ImageAnnularFilter")
        self.version("1.0")

        # Parse image center parameter
        try:
            assert('center' in self.params)
            c = eval(self.params['center'], {"__builtins__": None}, {})
            assert(type(c) is list)
            assert(len(c) == 2)
            assert(type(c[0]) is int)
            assert(type(c[1]) is int)
            self._center = c
        except:
            self._center = None

        # Parse inner diameter
        try:
            assert('inner' in self.params)
            c = eval(self.params['inner'], {"__builtins__": None}, {})
            assert(type(c) is list)
            assert(len(c) > 0)
            assert(type(c[0]) in (int, float))
            if len(c) > 1:
                assert(type(c[1]) in (int, float))
                self._inner = [el ** 2 for el in c]
            else:
                self._inner = [c[0] ** 2, c[0] ** 2]
        except Exception, e:
            self.logger.error("[%s] Missing inner diameter parameter (Error: %s)", self.name(), e)
            self._inner = None

        # Parse inner diameter
        try:
            assert('outer' in self.params)
            c = eval(self.params['outer'], {"__builtins__": None}, {})
            assert(type(c) is list)
            assert(len(c) > 0)
            assert(type(c[0]) in (int, float))
            if len(c) > 1:
                assert(type(c[1]) in (int, float))
                self._outer = [el ** 2 for el in c]
            else:
                self._outer = [c[0] ** 2, c[0] ** 2]
        except Exception, e:
            self.logger.error("[%s] Missing outer diameter parameter (Error: %s)", self.name(), e)
            self._outer = None

        # Mask
        self._mask = None

        # Detected image size
        self._size = None

    def process(self, target, **kwargs):
        """ Filter the image leaving only the required annulus. """
        # Check target type
        if target.name() != 'Image':
            self.logger.warning("[%s] Input variable is not an image. Skipping.", self.name())
            return {'output': None}
        # Check that inner and outer diameter are defined
        if self._inner is None or self._outer is None:
            self.logger.warning("[%s] One of the required diameter is not set. Skipping.", self.name())
            return {'output': None}

        # If size has changed or mask is not defined, we prepare it
        if self._mask is None or target.value.shape[1:] != self._size:
            self._size = target.value.shape[1:]
            if self._center is None:
                self._center = [int(target.value.shape[2] / 2), int(target.value.shape[1] / 2)]

            # Build the mask
            y, x = np.ogrid[0:self._size[0], 0:self._size[1]]
            x -= self._center[0]
            y -= self._center[1]
            r_in = x ** 2 / self._inner[0] + y ** 2 / self._inner[1]
            r_out = x ** 2 / self._outer[0] + y ** 2 / self._outer[1]
            self._mask = np.int8(r_in > 1) * np.int8(r_out < 1)

        # Filter the image using the defined mask
        self.logger.debug("[%s] Image shape %s, Mask shape %s.", self.name(), target.value.shape, self._mask.shape)
        out = Image()
        out.value = np.copy(target.value) * np.tile(self._mask, (target.value.shape[0], 1, 1))
        return {'output': out}

    @staticmethod
    def configure():
        """ Return parameters configuration. """
        delegates = {}

        # Center of the annulus. If not specified assumes the center of the image
        delegates['center'] = {
            'mandatory': False,
            'type': 'expr',
            'dtype': 'list>int',
            'label': 'Center',
            'delegate': {
                'type': 'RangeInputDelegate',
                'm': 1,
                'class': 'point'
            }
        }

        # Annulus inner diameter
        delegates['inner'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'list>num',
            'label': 'Inner diameter',
            'delegate': {
                'type': 'RangeInputDelegate',
                'm': 1,
                'class': 'incomplete'
            }
        }

        # Annulus inner diameter
        delegates['outer'] = {
            'mandatory': True,
            'type': 'expr',
            'dtype': 'list>num',
            'label': 'Outer diameter',
            'delegate': {
                'type': 'RangeInputDelegate',
                'm': 1,
                'class': 'incomplete'
            }
        }

        return delegates