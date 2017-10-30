'''
    QBI Meunier Tracker APP: setup.py (Windows 64bit MSI)
    *******************************************************************************
    Copyright (C) 2015  QBI Software, The University of Queensland

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''
#
# Step 1. Build first
#   python setup.py build
# View build dir contents
# Step 2. Create MSI distribution (Windows)
#   python setup.py bdist_msi
# View dist dir contents

application_title = 'QBI MSD Analysis'
main_python_file = 'appgui.py'

import sys
import os
from cx_Freeze import setup, Executable
from os.path import join
#devhome
#venvpython = 'D:\\python_venv\\scipyenv\\Lib\\site-packages'
#mainpython = 'C:\\Users\\lizcw\\AppData\\Local\\Programs\\Python\\Python35'
#devwork
venvpython = 'D:\\Dev\\python\\scipyenv\\Lib\\site-packages'
mainpython = 'D:\\Programs\\Python35'

os.environ['TCL_LIBRARY'] = join(mainpython,'tcl','tcl8.6')
os.environ['TK_LIBRARY'] = join(mainpython,'tcl','tk8.6')
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

build_exe_options = {
    'includes' : [],
    'excludes': [],
    'packages' : ['tkinter','seaborn','numpy.core._methods','numpy.lib.format', 'matplotlib.backends.backend_tkagg'],
    'include_files' : ['noname.py','resources/',
                       (join(venvpython, 'scipy','special','_ufuncs.cp35-win_amd64.pyd'),'_ufuncs.pyd')],
    'include_msvcr' : 1
   }
# [Bad fix but only thing that works] NB To add Shortcut working dir - change cx_freeze/windist.py Line 61 : last None - > 'TARGETDIR'
setup(
        name = application_title,
        version = '1.0',
        description = 'MSD Analysis scripts with GUI',
        long_description=open('README.md').read(),
        author='Liz Cooper-Williams, QBI',
        author_email='e.cooperwilliams@uq.edu.au',
        maintainer='QBI Custom Software, UQ',
        maintainer_email='qbi-dev-admin@uq.edu.au',
        url='http://github.com/QBI-Software/MSDAnalysis',
        license='GNU General Public License (GPL)',
        options = {'build_exe' : build_exe_options,},
        executables = [Executable(main_python_file, base = base, targetName='msdanalysis.exe',icon='resources/chart128.ico',
        shortcutName=application_title, shortcutDir='DesktopFolder')]
)

