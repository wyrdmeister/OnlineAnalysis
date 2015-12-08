#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Online Analysis - OA GUI Setup

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

import sys
import os
from distutils.core import setup


scripts = ['bin/OAEditor', 'bin/OAOffline', 'bin/OAControl']
packages = ['OAGui', 'OAGui.Ui',
            'OAGui.Editor', 'OAGui.Editor.Ui',
            'OAGui.Offline', 'OAGui.Offline.Ui',
            'OAGui.Control', 'OAGui.Control.Ui']
links = ['misc/OAControl.desktop', 'misc/OAEditor.desktop', 'misc/OAOffline.desktop']
icons = ['src/Images/oa_online.png', 'src/Images/oa_offline.png', 'src/Images/oa_editor.png']
icons_win = ['src/Images/oa_online.ico', 'src/Images/oa_offline.ico', 'src/Images/oa_editor.ico']

if "install" in sys.argv:
    try:
        import PyTango
    except ImportError:
        print "Cannot find PyTango. The OAControl GUI will not be installed."
        scripts.remove('bin/OAControl')
        packages.remove('OAGui.Control')
        packages.remove('OAGui.Control.Ui')
        links.remove('misc/OAControl.desktop')
        icons.remove('src/Images/oa_online.png')
        icons_win.remove('src/Images/oa_online.ico')
    except Exception as e:
        print "Unexpected exception: ", e
        exit(-1)

if os.name == 'posix':
    data_files = [('/usr/share/applications', links),
                  ('/usr/local/share/icons', icons)]
else:
    data_files = [('icons', icons_win)]

if "sdist" in sys.argv or "" in sys.argv:
    # Compile Ui and resources
    from subprocess import call
    import os
    call("bash " + os.path.dirname(os.path.abspath(__file__)) + "/src/Ui/build_ui", shell=True)
    call("bash " + os.path.dirname(os.path.abspath(__file__)) + "/src/Control/Ui/build_ui", shell=True)
    call("bash " + os.path.dirname(os.path.abspath(__file__)) + "/src/Editor/Ui/build_ui", shell=True)
    call("bash " + os.path.dirname(os.path.abspath(__file__)) + "/src/Offline/Ui/build_ui", shell=True)


setup(name='OAGui',
      version='1.1.0',
      description='Online Analysis GUI',
      author='Michele Devetta',
      author_email='michele.devetta@gmail.com',
      license='GPLv3',
      url='https://github.com/wyrdmeister/OnlineAnalysis',
      packages=packages,
      package_dir={'OAGui': 'src'},
      scripts=scripts,
      install_requires=[
        "PyQt4 >= 4.7",
        "h5py >= 1.8",
        "numpy >= 1.5",
        "matplotlib >= 1",
        'OACommon == 1.1.0',
      ],
      data_files=data_files,
     )