__author__ = "Evgeniy Efremov aka jhekasoft"

import os
import sys
import platform
import shutil
import re
import subprocess
import urllib.request
from packages.colorama import Style

class InsteadManagerConsole(object):

    def __init__(self, instead_manager):
        self.instead_manager = instead_manager

    def print_game_list(self, game_list: int, verbose: bool):
        for game in game_list:
            if verbose:
                self.out("%s%s%s (%s) %s\n%s%s%s %s [%s]\nDescription URL: %s\nURL: %s\n" % (
                    Style.BRIGHT, game['title'], Style.RESET_ALL,
                    game['lang'], self.instead_manager.size_format(int(game['size'])),
                    Style.BRIGHT, game['name'], Style.RESET_ALL,
                    game['version'],
                    game['repository_filename'], game['descurl'], game['url']
                ))
            else:
                self.out("%s %s%s%s %s" % (
                    game['title'],
                    Style.BRIGHT, game['name'], Style.RESET_ALL,
                    self.instead_manager.size_format(int(game['size']))
                ))

    def out(self, text):
        print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))

    def is_ansi_output(self):
        if (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()) or ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
            if platform.system()=='Windows' and not ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
                return False
            else:
                return True

            return False

    def update_repositories_action(self):
        self.out('Updating repositories...')

        for repository in self.instead_manager.repositories:
            self.out('Downloading %s ...' % repository['url'])
            filename = os.path.join(self.instead_manager.base_path, 'repositories', repository['name']+'.xml')
            urllib.request.urlretrieve(repository['url'], filename)

    def list_action(self, verbose: bool):
        game_list = self.instead_manager.get_sorted_game_list()
        self.print_game_list(game_list, verbose)

    def search_action(self, search: str, verbose: bool):
        game_list = self.instead_manager.get_sorted_game_list()

        filtered_game_list = []
        search_regex = '.*%s.*' % re.escape(search)
        for game in game_list:
            if re.search(search_regex, game['title'], re.IGNORECASE) or re.search(search_regex, game['name'], re.IGNORECASE):
                filtered_game_list.append(game)

        self.print_game_list(filtered_game_list, verbose)

    def install_action(self, name: str, run: str, verbose: bool):
        game_list = self.instead_manager.get_sorted_game_list()

        search_regex = '.*%s.*' % re.escape(name)
        for game in game_list:
            if re.search(search_regex, game['title'], re.IGNORECASE) or re.search(search_regex, game['name'], re.IGNORECASE):
                # Downloading game to the temp file
                self.out('Downloading %s ...' % game['url'])
                tmp_game_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'games')
                game_tmp_filename = os.path.join(tmp_game_path, 'tmp_'+game['name']+'.part')
                result = urllib.request.urlretrieve(game['url'], game_tmp_filename)

                base_game_filename = self.instead_manager.get_response_filename(result[1], game['url']);
                game_filename = '%s%s' % (tmp_game_path, base_game_filename)

                # Copying game to the file with normal name
                shutil.copy(game_tmp_filename, game_filename)
                os.remove(game_tmp_filename)

                # Installing game
                self.out('%s %s%s%s %s installing...' % (
                    game['title'],
                    Style.BRIGHT, game['name'], Style.RESET_ALL,
                    game['version']
                ))
                # Quit after installing or run game
                quit = ' -quit'
                if run:
                    quit = ''
                print('%s -install "%s"%s' % (self.instead_manager.interpreter_command, game_filename, quit))
                return_code = subprocess.call('%s -install "%s"%s' % (self.instead_manager.interpreter_command, game_filename, quit), shell=True)

                if 0 == return_code:
                    self.out('Compete')

                os.remove(game_filename)
                break

    def local_list_action(self, verbose: bool):
        local_game_list = self.instead_manager.get_sorted_local_game_list()
        for local_game in local_game_list:
            self.out(local_game['name'])

    def run_action(self, name: str):
        self.out('Running %s ...' % name)

        self.instead_manager.run_game(name)

    def delete_action(self, name: str):
        game_folder_path = os.path.expanduser(self.instead_manager.games_path) + name
        game_idf_path = os.path.expanduser(self.instead_manager.games_path) + name + '.idf'
        if os.path.exists(game_folder_path):
            shutil.rmtree(game_folder_path)
            self.out("Folder '%s' has been deleted" % game_folder_path)
        elif os.path.exists(game_idf_path):
            os.unlink(game_idf_path)
            self.out("File '%s' has been deleted" % game_idf_path)
        else:
            self.out("Folder '%s' doesn't exist. Is name correct?" % game_folder_path)
