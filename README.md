instead-manager
===============

There is old version. `InsteadMan 2` is available here: http://github.com/jhekasoft/insteadman.

Manager for INSTEAD repositories. It's working on GNU/Linux, Windows and probably on the other UNIX-systems
(FreeBSD, MacOS etc).

INSTEAD site: http://instead.syscall.ru

More information at http://instead.syscall.ru/talk/index.php/175-instead-manager

Configuration
-------------

You can change configuration at the `instead-manager-settings.json` (`instead-manager-settings-win.json` for `Windows`).
Example:

```
{
    "repositories": [
        {"name": "official", "url": "http://instead-launcher.googlecode.com/svn/pool/game_list.xml"},
        {"name": "instead-games", "url": "http://instead-games.ru/xml.php"},
        {"name": "instead-games-sandbox", "url": "http://instead-games.ru/xml2.php"}
    ],
    "games_path": "~/.instead/games/",
    "interpreter_command": "instead"
}
```

For `Windows 64bit` system you should change `interpreter_command` path to the `Program Files (x86)`:

```
"interpreter_command": "\"C:\\Program Files (x86)\\Games\\Instead\\sdl-instead.exe\""
```

Command line interface
----------------------

![alt text](https://github.com/jhekasoft/instead-manager/raw/master/docs/images/instead-manager-cli.png "instead-manager CLI")

UNIX systems:

```
python3 instead-manager.py -h
```

Windows systems:

```
py -3.4 instead-manager.py -h
```

GUI
---

`tkinter` implementation.

![alt text](https://github.com/jhekasoft/instead-manager/raw/master/docs/images/instead-manager-tk.png "instead-manager tkinter")

UNIX systems:

```
python3 instead-manager-tk.py
```

Windows systems:

```
py -3.4 instead-manager-tk.py
```

Documentation
-------------

See it [here](docs/index.md).
