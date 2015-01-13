#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__title__ = 'instead-manager'
__version__ = "0.5"
__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
import json
import argparse
from packages.colorama import init as colorama_init
from instead_utils.manager import InsteadManager
from instead_utils.console import InsteadManagerConsole

parser = argparse.ArgumentParser(description='%s (INSTEAD games manager) %s' % (__title__, __version__))
parser.add_argument('-u', '--update-repositories', action='store_true',
                    help='update repositories')
parser.add_argument('-l', '--list', action='store_true',
                    help='list games')
parser.add_argument('-s', '--search', nargs='?', type=str,
                    help='search games')
parser.add_argument('-i', '--install', nargs='?', type=str,
                    help='install game by name or title')
parser.add_argument('-r', '--run', nargs='?', type=str, const='const',
                    help='run game')
parser.add_argument('-ll', '--local-list', action='store_true',
                    help='list installed games')
parser.add_argument('-d', '--delete', nargs='?', type=str,
                    help='delete installed game')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='detailed print')
parser.add_argument('-ansi', '--ansi-output', choices=['on', 'off', 'auto'], nargs='?', default='auto', const='auto',
                    help='ANSI escaped chars output')

args = parser.parse_args()

# Loading config from JSON-file
config_file = 'instead-manager-settings.json'
if InsteadManager.is_win():
    config_file = 'instead-manager-settings-win.json'

jsonSettingsData = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file))
settings = json.load(jsonSettingsData)
repositories = settings['repositories']
games_path = settings['games_path']
interpreter_command = settings['interpreter_command']
instead_manager = InsteadManager(games_path, os.path.dirname(os.path.realpath(__file__)), interpreter_command, repositories)
instead_manager_console = InsteadManagerConsole(instead_manager)


# Init colors (colorama)
strip = False
if 'off' == args.ansi_output or ('auto' == args.ansi_output and not instead_manager_console.is_ansi_output()):
    strip = True
colorama_init(strip=strip)

if args.update_repositories:
    instead_manager_console.update_repositories_action()

if args.list:
    instead_manager_console.list_action(args.verbose)
elif args.search:
    instead_manager_console.search_action(args.search, args.verbose)
elif args.install:
    instead_manager_console.install_action(args.install, args.run, args.verbose)
elif args.local_list:
    instead_manager_console.local_list_action(args.verbose)
elif args.run:
    instead_manager_console.run_action(args.run)
elif args.delete:
    instead_manager_console.delete_action(args.delete)
