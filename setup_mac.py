'''
    QBI Auto Analysis APP: setup_mac.py (Mac OSX package)
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

Usage:
    python setup_mac.py py2app --matplotlib-backends='-'


Notes:
    Clean on reruns:
    > rm -rf build dist __pycache__
    May need to use system python rather than virtualenv
    > /Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6 setup_mac.py py2app --matplotlib-backends='-' > build.log

    Macholib version=1.7 required to prevent endless recursions
    Specify matplotlib backends with '-'
'''
import sys
from os.path import join
from os import getcwd
#Self -bootstrapping https://py2app.readthedocs.io
# import ez_setup
# ez_setup.use_setuptools()


from runapp import __version__
from setuptools import setup
from plistlib import Plist

application_title = 'QBI SPT Auto Analysis'
exe_name='autoanalysis_spt'

# Add info to MacOSX plist
# plist = Plist.fromFile('Info.plist')
plist = dict(CFBundleDisplayName=application_title,
	         CFBundleName=exe_name,
             NSHumanReadableCopyright='Copyright (c) 2018 Queensland Brain Institute',
             CFBundleTypeIconFile='measure.ico.icns',
             CFBundleVersion=__version__
             )

APP = ['runapp.py']
DATA_FILES = ['resources', 'gui']
PARENTDIR= join(getcwd(),'.')
OPTIONS = {'argv_emulation': True,
           'plist': plist,
           'iconfile': 'resources/measure.ico.icns',
           'packages': ['scipy', 'wx','pandas','msdapp'],
           'includes':['six','appdirs','packaging','packaging.version','packaging.specifiers','packaging.requirements','os','numbers','future_builtins'],
           'bdist_base': join(PARENTDIR, 'build'),
           'dist_dir': join(PARENTDIR, 'dist'),
           }

setup( name=exe_name,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app','pyobjc-framework-Cocoa','numpy','scipy'],
)
