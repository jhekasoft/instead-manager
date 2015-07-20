i18n
====

Update messages.pot

```
python3 /Library/Frameworks/Python.framework/Versions/3.4/share/doc/python3.4/examples/Tools/i18n/pygettext.py -d messages instead-manager-tk.pyw
```

Clear build and dist dirs before building Windows and OS X packages
===================================================================

```
rm -rf build dist
```

Create Windows executable
=========================
Make it in Windows (32 bit).

1. Install `Python 3`.

2. Install `py2exe`:

```
py -3.4 -m pip install py2exe
```

3. Copy `msvcr100.dll` from C:\Windows\system32\msvcr100.dll to .\temp

4. Build:

```
py -3.4 setup.py py2exe
```

Look result at the `dist` directory.

Create OS X application
=======================

1. Install `Python 3`.

2. Install `py2app`.

3. Build:

```
python3 setup.py py2app
```

Look `INSTEAD Manager` application at the `dist` directory.
