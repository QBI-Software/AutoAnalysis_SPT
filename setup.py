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
# Step 1. Build exe (in PyCharm: Tools -> Run setup.py Task -> build)
#   python setup.py build
# View build dir contents - double-click autoanalysis_spt.exe to test run
# Step 2. Create MSI distribution (Windows) (in PyCharm: Tools -> Run setup.py Task -> bdist_msi)
#   python setup.py bdist_msi
# View dist dir contents - test run bdist_msi file
########
# NOTE: If error with bdist_msi, comment out lines #333-342 in cx_freeze\windist.py and change elif to if


application_title = 'QBI SPT Auto Analysis'
main_python_file = 'runapp.py'

import os
import sys
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
    'includes': ['idna.idnadata', "numpy", "plotly", "packaging.version","packaging.specifiers", "packaging.requirements","appdirs",'scipy.spatial.ckdtree'],
    'excludes': ['PyQt4', 'PyQt5'],
    'packages': ['scipy','seaborn', 'numpy.core._methods', 'numpy.lib.format', 'plotly','wx','importlib', 'pandas'],
    'include_files': ['resources/','gui/', (join(venvpython, 'scipy', 'special', '_ufuncs.cp36-win_amd64.pyd'), '_ufuncs.pyd')],
    'include_msvcr': 1
}

bdist_msi_options = {
    "skip_build": True,
    "upgrade_code": "{13252EEB-C257-41C6-9BC9-6CD4B4FD9D85}" #get uid from first installation regedit
    }

setup(
    name=application_title,
    version=__version__,
    description='Auto Analysis for SPT (Meunier,QBI)',
    long_description=open('README.md').read(),
    author='Liz Cooper-Williams, QBI',
    author_email='lcwsoftware@gmail.com',
    maintainer='QBI Custom Software, UQ',
    maintainer_email='qbi-dev-admin@uq.edu.au',
    url='http://github.com/QBI-Software/AutoAnalysis_SPT',
    license='GNU General Public License (GPL)',
    options={'build_exe': build_exe_options, 'bdist_msi': bdist_msi_options},
    executables=[Executable(main_python_file,
                            base=base,
                            target_name='autoanalysis_spt.exe',
                            icon='resources/measure.ico',
                            shortcut_name=application_title,
                            shortcut_dir='DesktopFolder')]
)

