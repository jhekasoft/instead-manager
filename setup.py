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
    OPTIONS = {
        'argv_emulation': True,
        'packages': ['packages'],
        'resources': ['resources', 'skeleton', 'locale', 'docs', 'messages.pot', 'README.md'],
        'iconfile': 'resources/images/logo.icns'
    }

    setup(
        name=app_name,
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
elif sys.platform == 'win32':
    import os
    import glob
    import py2exe
    import packages

    def find_data_files(source, target, patterns):
        """Locates the specified data-files and returns the matches
        in a data_files compatible format.

        http://www.py2exe.org/index.cgi/data_files

        source is the root of the source data tree.
            Use '' or '.' for current directory.
        target is the root of the target data tree.
            Use '' or '.' for the distribution directory.
        patterns is a sequence of glob-patterns for the
            files you want to copy.
        """
        if glob.has_magic(source) or glob.has_magic(target):
            raise ValueError("Magic not allowed in src, target")
        ret = {}
        for pattern in patterns:
            pattern = os.path.join(source, pattern)
            for filename in glob.glob(pattern):
                if os.path.isfile(filename):
                    targetpath = os.path.join(target, os.path.relpath(filename, source))
                    path = os.path.dirname(targetpath)
                    ret.setdefault(path, []).append(filename)
        return sorted(ret.items())

    # Reserve recipe
    # import sys
    # sys.path.append('./packages')

    options = {'includes': ['xml'], 'packages': ['packages']}
    data_files = find_data_files('', '', [
        'resources/*/*',
        'resources/*/*/*',
        'skeleton/*',
        'locale/*/*/*',
        'docs/*',
        'messages.pot',
        'README.md'
    ])
    data_files += find_data_files('temp', '', ['msvcr100.dll'])
    setup(
        name=app_name,
        # console=[main_script],
        windows=[
            {
                'script': main_script,
                'icon_resources': [(1, 'resources/images/logo.ico')],
            }
        ],
        options={'py2exe': options},
        data_files=data_files,
        setup_requires=['py2exe'],
    )
