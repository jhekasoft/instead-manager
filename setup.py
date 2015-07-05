"""
py2app/py2exe build script for INSTEAD Manager.

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows, isn't implemented yet):
    python setup.py py2exe

For GNU/Linux (and other free UNIX) please use Makefile.
"""

import sys
from setuptools import setup

app_name = 'INSTEAD Manager'
main_script = 'instead-manager-tk.pyw'

if sys.platform == 'darwin':
    APP = [main_script]
    DATA_FILES = ['instead-manager-tk.pyw']
    OPTIONS = {'argv_emulation': True, 'packages': ['packages'], 'resources': ['resources', 'skeleton', 'locale', 'docs', 'messages.pot', 'README.md'],
               'iconfile': 'resources/images/logo.icns'}

    setup(
        name=app_name,
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
elif sys.platform == 'win32':
    pass
