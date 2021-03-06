#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Online Analysis - OA Server Setup

Version 1.1

Michele Devetta (c) 2015


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

from distutils.core import setup

setup(name='OAServer',
      version='1.1.0',
      description='Online Analysis Server Components',
      author='Michele Devetta',
      author_email='michele.devetta@gmail.com',
      license='GPLv3',
      url='https://github.com/wyrdmeister/OnlineAnalysis',
      packages=['OAServer'],
      package_dir={'OAServer': 'src'},
      install_requires=[
          'PyTango >= 8',
          'OACommon == 1.1.0',
          'h5py >= 1.8',
          'numpy >= 1.5'],
     )