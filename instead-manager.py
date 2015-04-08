#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__title__ = 'instead-manager'
__version__ = "0.15"
__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
import sys
import errno
import platform
import argparse

from packages.colorama import init as colorama_init, Style, Fore
from manager import InsteadManagerFreeUnix, InsteadManagerWin, InsteadManagerMac, InsteadManagerHelper


class InsteadManagerConsole(object):

    def __init__(self, instead_manager):
        self.instead_manager = instead_manager

    def out(self, text):
        print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))

    def out_success(self, text, exit=False):
        self.out(Fore.GREEN + text + Fore.RESET)

        if exit:
            sys.exit()

    def out_fail(self, text, exit=False):
        self.out(Fore.RED + text + Fore.RESET)

        if exit:
            sys.exit(errno.EFAULT)

    def print_game_list(self, game_list: int, verbose: bool):
        for game in game_list:
            if verbose:
                self.out("%s%s%s (%s) %s\n%s%s%s %s [%s]\nDescription URL: %s\nURL: %s\n" % (
                    Style.BRIGHT + Fore.YELLOW, game['title'], Fore.RESET + Style.RESET_ALL,
                    game['lang'], self.instead_manager.size_format(int(game['size'])),
                    Style.BRIGHT, game['name'], Style.RESET_ALL,
                    game['version'],
                    game['repository_filename'], game['descurl'], game['url']
                ))
            else:
                self.out("%s%s%s %s%s%s %s" % (
                    Style.BRIGHT + Fore.YELLOW, game['title'], Fore.RESET + Style.RESET_ALL,
                    Style.BRIGHT, game['name'], Style.RESET_ALL,
                    self.instead_manager.size_format(int(game['size']))
                ))

    def is_ansi_output(self):
        if (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()) or ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
            if platform.system()=='Windows' and not ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
                return False
            else:
                return True

            return False

    def download_status_callback(self, blocknum, blocksize, totalsize):
        loadedsize = blocknum * blocksize
        if loadedsize > totalsize:
            loadedsize = totalsize
        if totalsize > 0:
            percent = loadedsize * 1e2 / totalsize
            s = "\r%5.1f%% %s / %s     " % (
                percent, self.instead_manager.size_format(loadedsize), self.instead_manager.size_format(totalsize))
            sys.stderr.write(s)
            if loadedsize >= totalsize:
                # The end
                sys.stderr.write("\n")

    def begin_downloading_callback(self, game):
        self.out('Downloading %s ...' % game['url'])

    def begin_installation_callback(self, game):
        self.out('%s %s%s%s %s installing...' % (
            game['title'],
            Style.BRIGHT, game['name'], Style.RESET_ALL,
            game['version']
        ))

    def get_sorted_game_list(self):
        try:
            return self.instead_manager.get_sorted_game_list()
        except Exception as e:
            self.out_fail(e.__str__(), True)

    def update_repositories_action(self):
        self.instead_manager.\
            update_repositories(download_status_callback=self.download_status_callback,
                                begin_repository_downloading_callback=self.begin_repository_downloading_callback)

    def begin_repository_downloading_callback(self, repository):
        self.out('Downloading %s...' % (Style.BRIGHT + repository['url'] + Style.RESET_ALL))

    def list_action(self, verbose: bool):
        game_list = self.get_sorted_game_list()
        self.print_game_list(game_list, verbose)

    def search_action(self, search: str=None, repository: str=None, lang: str=None, verbose: bool=False):
        game_list = self.get_sorted_game_list()
        filtered_game_list = self.instead_manager.filter_games(game_list, search, repository, lang)

        self.print_game_list(filtered_game_list, verbose)

    def install_action(self, name: str, run: str, verbose: bool):
        game = None

        game_list = self.get_sorted_game_list()

        # Search exactly by name
        for game_list_item in game_list:
            if game_list_item['name'] == name:
                game = game_list_item

        if game is None:
            # Search exactly by title
            for game_list_item in game_list:
                if game_list_item['title'] == name:
                    game = game_list_item

        if game is None:
            filtered_game_list = self.instead_manager.filter_games(game_list, name)
            if filtered_game_list and len(filtered_game_list) > 0:
                game = filtered_game_list[0]

        if game is None:
            self.out_fail('Game has not found', exit=True)

        installed =\
            self.instead_manager.install_game(game, run,
                                              download_status_callback=self.download_status_callback,
                                              begin_downloading_callback=self.begin_downloading_callback,
                                              begin_installation_callback=self.begin_installation_callback)

        if installed:
            self.out_success('Compete', exit=True)

        self.out_fail('Game has not been installed', exit=True)

    def local_list_action(self, verbose: bool):
        local_game_list = self.instead_manager.get_sorted_local_game_list()
        for local_game in local_game_list:
            self.out(Style.BRIGHT + local_game['name'] + Style.RESET_ALL)

    def run_action(self, name: str):
        self.out('Running %s ...' % name)

        run = self.instead_manager.run_game(name)

        if not run:
            self.out_fail("Game hasn't run", exit=True)

        self.out_success("Game has run")

    def delete_action(self, name: str):
        deleted = self.instead_manager.delete_game(name)
        if not deleted:
            self.out_fail("Game hasn't been deleted", exit=True)

        self.out_success("Game has been deleted")

    def check_instead_interpreter_action(self, verbose: bool):
        check, info = self.instead_manager.check_instead_interpreter_with_info()
        if check:
            self.out_success("INSTEAD interpreter is correctly configured. INSTEAD version: %s" % info, exit=True)

        self.out_fail("INSTEAD interpreter is not correctly configured.\n%s" % info, exit=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='%s (INSTEAD Manager) %s' % (__title__, __version__))
    parser.add_argument('-u', '--update-repositories', action='store_true',
                        help='update repositories')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list games')
    parser.add_argument('-s', '--search', nargs='?', type=str,
                        help='search games')
    parser.add_argument('-rep', '--filter-repository', nargs='?', type=str,
                        help='filter by repository')
    parser.add_argument('-lang', '--filter-language', nargs='?', type=str,
                        help='filter by language')
    parser.add_argument('-i', '--install', nargs='?', type=str,
                        help='install game by name or title')
    parser.add_argument('-r', '--run', nargs='?', type=str, const='const',
                        help='run game')
    parser.add_argument('-ll', '--local-list', action='store_true',
                        help='list installed games')
    parser.add_argument('-d', '--delete', nargs='?', type=str,
                        help='delete installed game')
    parser.add_argument('-ci', '--check-instead', action='store_true',
                        help='checks INSTEAD interpreter')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='detailed print')
    parser.add_argument('-ansi', '--ansi-output', choices=['on', 'off', 'auto'], nargs='?', default='auto', const='auto',
                        help='ANSI escaped chars output')

    # Print help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    try:
        base_path = os.path.dirname(os.path.realpath(__file__))
    except NameError:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    if InsteadManagerHelper.is_win():
        instead_manager = InsteadManagerWin(base_path)
    elif InsteadManagerHelper.is_mac():
        instead_manager = InsteadManagerMac(base_path)
    else:
        instead_manager = InsteadManagerFreeUnix(base_path)

    instead_manager_console = InsteadManagerConsole(instead_manager)


    # Init colors (colorama)
    strip = False
    if 'off' == args.ansi_output or ('auto' == args.ansi_output and not instead_manager_console.is_ansi_output()):
        strip = True
    colorama_init(strip=strip)

    if args.update_repositories:
        instead_manager_console.update_repositories_action()

    if args.check_instead:
            instead_manager_console.check_instead_interpreter_action(args.verbose)
    elif args.list:
        instead_manager_console.list_action(args.verbose)
    elif args.search or args.filter_repository or args.filter_language:
        instead_manager_console.search_action(search=args.search, repository=args.filter_repository,
                                              lang=args.filter_language, verbose=args.verbose)
    elif args.install:
        instead_manager_console.install_action(args.install, args.run, args.verbose)
    elif args.local_list:
        instead_manager_console.local_list_action(args.verbose)
    elif args.run:
        instead_manager_console.run_action(args.run)
    elif args.delete:
        instead_manager_console.delete_action(args.delete)
