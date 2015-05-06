__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
import platform
import sys
import glob
import shutil
import subprocess
from xml.dom import minidom
import re
import urllib.request
import json
from abc import ABCMeta, abstractmethod

from packages.instead_manager.interpreter_finder import InsteadInterpreterFinder


class InsteadManager(object, metaclass=ABCMeta):
    skeleton_filename = 'instead-manager-settings.json'
    default_config_path = '~/.instead/manager/'
    default_config_filename = 'instead-manager-settings.json'

    def __init__(self, base_path, interpreter_finder: InsteadInterpreterFinder=None,
                 games_path=None, interpreter_command=None, repositories=None):
        self.base_path = base_path

        # TODO: replace by Configurator
        # Config path
        self.config_path = self.base_path
        if not os.path.isfile(os.path.join(self.config_path, self.default_config_filename)):
            self.config_path = os.path.expanduser(self.default_config_path)
        self.check_and_create_path(self.config_path)
        self.config_filepath = os.path.join(self.config_path, self.default_config_filename)

        self.interpreter_finder = interpreter_finder

        if not os.path.isfile(os.path.join(self.config_path, self.default_config_filename)):
            shutil.copyfile(os.path.join(self.base_path, 'skeleton', self.skeleton_filename), self.config_filepath)

            # Find and write interpreter command
            interpreter_command = self.interpreter_finder.find_interpreter()
            if interpreter_command:
                tmp_settings = self.read_settings()
                tmp_settings['interpreter_command'] = interpreter_command
                json_settings_file = open(self.config_filepath, "w")
                json.dump(tmp_settings, json_settings_file, indent=4)
                json_settings_file.close()

        if None in (games_path, interpreter_command, repositories):
            settings = self.read_settings()

        self.games_path = os.path.expanduser(games_path if games_path else settings['games_path'])
        self.interpreter_command = interpreter_command if interpreter_command else settings['interpreter_command']

        # Repositories
        self.repositories = repositories if repositories else settings['repositories']
        self.repositories_directory = os.path.join(self.config_path, 'repositories')
        self.check_and_create_path(self.repositories_directory)

        # Temp downloaded game path
        self.tmp_game_path = os.path.join(self.config_path, 'games')
        self.check_and_create_path(self.tmp_game_path)

    def check_and_create_path(self, path):
        if not os.path.isdir(path):
            return os.makedirs(path)

        return True

    def read_settings(self):
        # TODO: replace by Configurator
        """
        Loading config from JSON-file

        :return:
        """
        json_settings_data = open(self.config_filepath)

        return json.load(json_settings_data)

    def get_repository_files(self):
        files = glob.glob('%s/*.xml' % self.repositories_directory)
        if not files:
            raise RepositoryFilesAreMissingError('No repository files in %s. Please try to update it.' %
                                                 self.repositories_directory)

        return files

    def get_game_list(self):
        files = self.get_repository_files()

        game_list = []
        for file in files:
            game_list.extend(self.get_games_from_file(file))

        return game_list

    def get_sorted_game_list(self):
        game_list = self.get_game_list()
        game_list.sort(key=lambda game: (game['title']))

        return game_list

    def get_games_from_file(self, file_path):
        xml_doc = minidom.parse(file_path)
        xml_game_list = xml_doc.getElementsByTagName('game')

        repository_filename = os.path.basename(file_path)

        game_list_unsorted = []
        for game in xml_game_list:
            # TODO: make iteration for fields
            # TODO: make game as object
            title = game.getElementsByTagName("title")[0]
            name = game.getElementsByTagName("name")[0]
            version = game.getElementsByTagName("version")[0]
            url = game.getElementsByTagName("url")[0]
            size = game.getElementsByTagName("size")[0]
            descurl = game.getElementsByTagName("descurl")[0]
            langs = self.xml_game_parse_languages(game)
            game_list_unsorted.append({
                'title': title.firstChild.data,
                'name': name.firstChild.data,
                'version': version.firstChild.data,
                'langs': self.xml_game_parse_languages(game),
                'lang': ', '.join(langs),
                'url': url.firstChild.data,
                'size': size.firstChild.data,
                'descurl': descurl.firstChild.data,
                'repository_filename': repository_filename,
                'installed': False,
            })

        return game_list_unsorted

    def xml_game_parse_languages(self, game):
        raw_langs = []

        langs_elements = game.getElementsByTagName("langs")
        if langs_elements:
            # format: <langs><lang>en</lang><lang>ru</lang></langs>
            lang_elements = langs_elements[0].getElementsByTagName("lang")
            for lang_element in lang_elements:
                raw_langs.append(lang_element.firstChild.data)
        else:
            # format: <lang>en,ru</lang>
            lang_element = game.getElementsByTagName("lang")[0]
            raw_langs = lang_element.firstChild.data.split(',')

        langs = list(map(lambda lang: lang.strip(), raw_langs))
        return langs


    def get_local_game_list(self):
        files = glob.glob('%s*' % self.games_path)

        local_game_list = []
        for file in files:
            game_name = os.path.basename(file)
            match = re.search('(.*)\.idf$', game_name, re.IGNORECASE)
            if match:
                game_name = match.groups()[0]
            local_game_list.append({'name': game_name})

        return local_game_list

    def get_sorted_local_game_list(self):
        local_game_list = self.get_local_game_list()
        local_game_list.sort(key=lambda game: (game['name']))

        return local_game_list

    def get_combined_game_list(self):
        try:
            game_list = self.get_sorted_game_list()
        except Exception:
            game_list = []

        local_game_list = self.get_sorted_local_game_list()

        local_game_names = []
        for local_game in local_game_list:
            local_game_names.append(local_game['name'])

        only_local_game_names = local_game_names[:]

        # Search installed games
        for game in game_list:
            if game['name'] in local_game_names:
                game['installed'] = True
                if game['name'] in only_local_game_names:
                    only_local_game_names.remove(game['name'])
            else:
                game['installed'] = False

        # Local games which are missing in repositories
        for only_local_game_name in only_local_game_names:
            game_list.append({
                'title': only_local_game_name,
                'name': only_local_game_name,
                'version': '',
                'langs': [],
                'lang': '',
                'url': '',
                'size': 0,
                'descurl': '',
                'repository_filename': '',
                'installed': True,
            })

        return game_list

    def get_sorted_combined_game_list(self):
        game_list = self.get_combined_game_list()
        game_list.sort(key=lambda game: (game['title']))

        return game_list

    def get_gamelist_repositories(self, game_list):
        repositories = []
        for game in game_list:
            if game['repository_filename'] and game['repository_filename'] not in repositories:
                repositories.append(game['repository_filename'])

        return repositories

    def get_gamelist_langs(self, game_list):
        langs = []
        for game in game_list:
            if game['langs']:
                for game_lang in game['langs']:
                    if game_lang not in langs:
                        langs.append(game_lang)

        return langs

    def is_found_keyword(self, game, value):
        search_regex = '.*%s.*' % re.escape(value)
        return re.search(search_regex, game['title'], re.IGNORECASE) or re.search(search_regex, game['name'], re.IGNORECASE)

    def is_found_repository(self, game, value):
        return game['repository_filename'] == value or game['repository_filename'] == value + '.xml'

    def is_found_lang(self, game, value):
        return value in game['langs']

    def is_found_only_installed(self, game, value):
        return value == game['installed']

    def filter_games(self, game_list, keyword: str=None, repository: str=None, lang: str=None, only_installed=False):
        if keyword:
            game_list = self.filter_by(game_list, self.is_found_keyword, keyword)
        if repository:
            game_list = self.filter_by(game_list, self.is_found_repository, repository)
        if lang:
            game_list = self.filter_by(game_list, self.is_found_lang, lang)
        if only_installed:
            game_list = self.filter_by(game_list, self.is_found_only_installed, only_installed)

        return game_list

    def filter_by(self, game_list, found_callback, value):
        filtered_game_list = []

        for game in game_list:
            found = found_callback(game, value)
            if found:
                filtered_game_list.append(game)

        return filtered_game_list

    def update_repositories(self, download_status_callback=None, begin_repository_downloading_callback=None,
                            end_downloading_callback=None):
        for repository in self.repositories:
            if begin_repository_downloading_callback:
                begin_repository_downloading_callback(repository)

            filename = os.path.join(self.repositories_directory, repository['name']+'.xml')

            try:
                urllib.request.urlretrieve(repository['url'], filename, download_status_callback)
            except Exception:
                pass

        if end_downloading_callback:
            end_downloading_callback()

        return True

    def install_game(self, game, run=False, download_status_callback=None,
                     begin_downloading_callback=None, begin_installation_callback=None,
                     end_installation=None):

        # Downloading game to the temp file
        if begin_downloading_callback:
            begin_downloading_callback(game)

        game_tmp_filename = os.path.join(self.tmp_game_path, 'tmp_'+game['name']+'.part')
        result = urllib.request.urlretrieve(game['url'], game_tmp_filename, download_status_callback)

        base_game_filename = self.get_response_filename(result[1], game['url'])
        game_filename = '%s%s' % (self.tmp_game_path, base_game_filename)

        # Copying game to the file with normal name
        shutil.copy(game_tmp_filename, game_filename)
        os.remove(game_tmp_filename)

        # Game installation
        if begin_installation_callback:
            begin_installation_callback(game)

        quit_instead = ' -quit'
        if run:
            quit_instead = ''
        return_code = self.execute_install_game_command(game_filename, quit_instead)

        os.remove(game_filename)

        result = True
        if 0 != return_code:
            result = False

        if end_installation:
            end_installation(game, end_installation)

        return result

    def get_response_filename(self, http_message, url):
        filename = None

        content_disposition = http_message.get('Content-Disposition')
        if content_disposition:
            filename = re.findall("filename=(\S+)", content_disposition)[0].strip(' \t\n\r"\'')

        if not filename:
            filename = url.split('/')[-1]

        return filename

    def run_game(self, name):
        running_name = name

        # IDF check
        files = glob.glob('%s%s.idf' % (self.games_path, name))
        if len(files) > 0:
            running_name = running_name+'.idf'

        self.execute_run_game_command(running_name)
        return True

    def delete_game(self, name):
        game_folder_path = self.games_path + name
        game_idf_path = self.games_path + name + '.idf'
        if os.path.exists(game_folder_path):
            shutil.rmtree(game_folder_path)
            return True
            # self.out("Folder '%s' has been deleted" % game_folder_path)
        elif os.path.exists(game_idf_path):
            os.unlink(game_idf_path)
            return True
            # self.out("File '%s' has been deleted" % game_idf_path)

        return False
        # self.out("Folder '%s' doesn't exist. Is name correct?" % game_folder_path)

    def check_instead_interpreter_with_info(self):
        if self.interpreter_finder is not None:
            return self.interpreter_finder.check_interpreter(self.interpreter_command)

        return False, 'Interpreter finder is not set'

    def check_instead_interpreter(self):
        check, info = self.check_instead_interpreter_with_info()
        return check

    @abstractmethod
    def execute_run_game_command(self, game_name):
        pass

    @abstractmethod
    def execute_install_game_command(self, game_filename, quit_instead):
        pass

    @staticmethod
    def size_format(size):
        return InsteadManagerHelper.size_format(size)


class InsteadManagerFreeUnix(InsteadManager):
    def execute_run_game_command(self, game_name):
        command = '%s -game "%s" &>/dev/null' % (self.interpreter_command, game_name)
        subprocess.Popen(command, shell=True)

    def execute_install_game_command(self, game_filename, quit_instead):
        command = '%s -install "%s"%s' % (self.interpreter_command, game_filename, quit_instead)
        return subprocess.call(command, shell=True)

class InsteadManagerWin(InsteadManager):
    skeleton_filename = 'instead-manager-settings-win.json'
    default_config_path = '~\\Local Settings\\Application Data\\instead\\manager\\'

    def execute_run_game_command(self, game_name):
        command = '%s -game "%s"' % (self.interpreter_command, game_name)
        subprocess.Popen(command, shell=True)

    def execute_install_game_command(self, game_filename, quit_instead):
        command = '%s -install "%s"%s' % (self.interpreter_command, game_filename, quit_instead)
        return subprocess.call(command, shell=True)


class InsteadManagerMac(InsteadManager):
    skeleton_filename = 'instead-manager-settings-mac.json'

    def execute_run_game_command(self, game_name):
        command = 'export LC_CTYPE=C; open -a "%s" --args -game "%s"' % (self.interpreter_command, game_name)
        subprocess.Popen(command, shell=True)

    def execute_install_game_command(self, game_filename, quit_instead):
        command = '"%s" -install "%s"%s' % (self.interpreter_command, game_filename, quit_instead)
        return subprocess.call(command, shell=True)


class InsteadManagerHelper(object):
    @staticmethod
    def size_format(size):
        suffix = 'B'
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(size) < 1024.0:
                return "%3.1f%s%s" % (size, unit, suffix)
            size /= 1024.0
        return "%.1f%s%s" % (size, 'Yi', suffix)

    @staticmethod
    def is_win():
        return any(platform.win32_ver())

    @staticmethod
    def is_free_unix():
        return sys.platform.startswith('linux') or sys.platform.startswith('freebsd')

    @staticmethod
    def is_mac():
        return 'darwin' == sys.platform


class RepositoryFilesAreMissingError(Exception):
    pass
