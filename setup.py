'''
    QBI MSD Analysis APP: setup.py (Windows 64bit MSI)
    *******************************************************************************
    Copyright (C) 2017  QBI Software, The University of Queensland

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
####
# Issues with scipy and cx-freeze -> https://stackoverflow.com/questions/32432887/cx-freeze-importerror-no-module-named-scipy
# 1. changed cx_Freeze/hooks.py scipy.lib to scipy._lib (line 560)
#then run setup.py build
# 2. changed scipy/spatial cKDTree.cp35-win_amd64.pyd to ckdtree.cp35-win_amd64.pyd
# 3. change Plot.pyc to plot.pyc in multiprocessing
# test with exe
# then run bdist_msi
# create 64bit from 32bit python with python setup.py build --plat-name=win-amd64
# NB To add Shortcut working dir - change cx_freeze/windist.py Line 61 : last None - > 'TARGETDIR'

application_title = 'QBI SPT Auto Analysis'
main_python_file = 'runapp.py'

import os
import sys
import shutil
from os.path import join
from cx_Freeze import setup, Executable
from runapp import __version__

venvpython = join(sys.prefix,'Lib','site-packages')
mainpython = "D:\\Programs\\Python36"

os.environ['TCL_LIBRARY'] = join(mainpython, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = join(mainpython, 'tcl', 'tk8.6')
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

build_exe_options = {
    'includes': ['idna.idnadata', "numpy", "plotly", "packaging.version","packaging.specifiers", "packaging.requirements","appdirs",'scipy.spatial.cKDTree'],
    'excludes': ['PyQt4', 'PyQt5'],
    'packages': ['scipy','seaborn', 'numpy.core._methods', 'numpy.lib.format', 'plotly','wx'],
    'include_files': ['resources/','gui/', (join(venvpython, 'scipy', 'special', '_ufuncs.cp36-win_amd64.pyd'), '_ufuncs.pyd')],
    'include_msvcr': 1
}

bdist_msi_options = {
    "upgrade_code": "{13252EEB-C257-41C6-9BC9-6CD4B4FD9D85}" #get uid from first installation regedit
    }

setup(
    name=application_title,
    version=__version__,
    description='Auto Analysis for SPT (Meunier,QBI)',
    long_description=open('README.md').read(),
    author='Liz Cooper-Williams, QBI',
    author_email='e.cooperwilliams@uq.edu.au',
    maintainer='QBI Custom Software, UQ',
    maintainer_email='qbi-dev-admin@uq.edu.au',
    url='http://github.com/QBI-Software/AutoAnalysis_SPT',
    license='GNU General Public License (GPL)',
    options={'build_exe': build_exe_options, 'bdist_msi': bdist_msi_options},
    executables=[Executable(main_python_file,
                            base=base,
                            targetName='autoanalysis_spt.exe',
                            icon='resources/measure.ico',
                            shortcutName=application_title,
                            shortcutDir='DesktopFolder')]
)

#Rename ckdtree
shutil.move(join('build','exe.win-amd64-3.6','lib','scipy','spatial','cKDTree.cp36-win_amd64.pyd'), join('build','exe.win-amd64-3.6','lib','scipy','spatial','ckdtree.pyd'))
shutil.copyfile(join('build','exe.win-amd64-3.6','lib','scipy','spatial','ckdtree.pyd'), join('build','exe.win-amd64-3.6','lib','scipy','spatial','ckdtree.cp36-win_amd64.pyd'))
