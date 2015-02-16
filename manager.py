__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
import platform
import glob
import shutil
import subprocess
from xml.dom import minidom
import re
import urllib.request
import json


class InsteadManager(object):
    default_config_filename = 'instead-manager-settings.json'
    run_game_command_postfix = ' &>/dev/null'

    def __init__(self, base_path, games_path=None, interpreter_command=None, repositories=None):
        self.base_path = base_path

        if None in (games_path, interpreter_command, repositories):
            settings = self.read_settings()

        self.games_path = games_path if games_path else settings['games_path']
        self.interpreter_command = interpreter_command if interpreter_command else settings['interpreter_command']
        self.repositories = repositories if repositories else settings['repositories']
        self.repositories_directory = '%s/repositories/' % self.base_path

    def read_settings(self):
        """
        Loading config from JSON-file

        :return:
        """
        json_settings_data = open(os.path.join(self.base_path, self.default_config_filename))

        return json.load(json_settings_data)

    def get_sorted_game_list(self):
        files = glob.glob('%s/*.xml' % self.repositories_directory)
        if not files:
            raise RepositoryFilesAreMissingError('No repository files in %s. Please try to update it.' %
                                                 self.repositories_directory)

        game_list = []
        for file in files:
            game_list.extend(self.get_games_from_file(file))

        game_list.sort(key=lambda game: (game['title']))

        return game_list

    def get_games_from_file(self, file_path):
        xml_doc = minidom.parse(file_path)
        xml_game_list = xml_doc.getElementsByTagName('game')

        repository_filename = os.path.basename(file_path)

        game_list_unsorted = []
        for game in xml_game_list:
            # TODO: make iteration for fields
            title = game.getElementsByTagName("title")[0]
            name = game.getElementsByTagName("name")[0]
            version = game.getElementsByTagName("version")[0]
            lang = game.getElementsByTagName("lang")[0]
            url = game.getElementsByTagName("url")[0]
            size = game.getElementsByTagName("size")[0]
            descurl = game.getElementsByTagName("descurl")[0]
            game_list_unsorted.append({
                'title': title.firstChild.data,
                'name': name.firstChild.data,
                'version': version.firstChild.data,
                'lang': lang.firstChild.data,
                'url': url.firstChild.data,
                'size': size.firstChild.data,
                'descurl': descurl.firstChild.data,
                'repository_filename': repository_filename,
            })

        return game_list_unsorted

    def get_sorted_local_game_list(self):
        files = glob.glob('%s*' % os.path.expanduser(self.games_path))

        local_game_list = []
        for file in files:
            game_name = os.path.basename(file)
            match = re.search('(.*)\.idf$', game_name, re.IGNORECASE)
            if match:
                game_name = match.groups()[0]
            local_game_list.append({'name': game_name})

        local_game_list.sort(key=lambda game: (game['name']))

        return local_game_list

    def get_gamelist_repositories(self, game_list):
        repositories = []
        for game in game_list:
            if game['repository_filename'] not in repositories:
                repositories.append(game['repository_filename'])

        return repositories

    def get_gamelist_langs(self, game_list):
        langs = []
        for game in game_list:
            if game['lang'] not in langs:
                langs.append(game['lang'])

        return langs

    def is_found_keyword(self, game, value):
        search_regex = '.*%s.*' % re.escape(value)
        return re.search(search_regex, game['title'], re.IGNORECASE) or re.search(search_regex, game['name'], re.IGNORECASE)

    def is_found_repository(self, game, value):
        return game['repository_filename'] == value or game['repository_filename'] == value + '.xml'

    def is_found_lang(self, game, value):
        return game['lang'] == value

    def filter_games(self, game_list, keyword: str=None, repository: str=None, lang: str=None):
        if keyword:
            game_list = self.filter_by(game_list, self.is_found_keyword, keyword)
        if repository:
            game_list = self.filter_by(game_list, self.is_found_repository, repository)
        if lang:
            game_list = self.filter_by(game_list, self.is_found_lang, lang)

        return game_list

    def filter_by(self, game_list, found_callback, value):
        filtered_game_list = []

        for game in game_list:
            found = found_callback(game, value)
            if found:
                filtered_game_list.append(game)

        return filtered_game_list

    def update_repositories(self, download_status_callback=None, begin_repository_downloading_callback=None,
                            end_downloading=None):
        for repository in self.repositories:
            if begin_repository_downloading_callback:
                begin_repository_downloading_callback(repository)

            filename = os.path.join(self.base_path, 'repositories', repository['name']+'.xml')
            urllib.request.urlretrieve(repository['url'], filename, download_status_callback)

        if end_downloading:
            end_downloading()

        return True

    def install_game(self, game, run=False, download_status_callback=None,
                     begin_downloading_callback=None, begin_installation_callback=None,
                     end_installation=None):

        # Downloading game to the temp file
        if begin_downloading_callback:
            begin_downloading_callback(game)

        tmp_game_path = os.path.join(self.base_path, 'games')
        game_tmp_filename = os.path.join(tmp_game_path, 'tmp_'+game['name']+'.part')
        result = urllib.request.urlretrieve(game['url'], game_tmp_filename, download_status_callback)

        base_game_filename = self.get_response_filename(result[1], game['url'])
        game_filename = '%s%s' % (tmp_game_path, base_game_filename)

        # Copying game to the file with normal name
        shutil.copy(game_tmp_filename, game_filename)
        os.remove(game_tmp_filename)

        # Game installation
        if begin_installation_callback:
            begin_installation_callback(game)

        quit_instead = ' -quit'
        if run:
            quit_instead = ''
        return_code = subprocess.call(
            '%s -install "%s"%s' % (self.interpreter_command, game_filename, quit_instead), shell=True)

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
        files = glob.glob('%s%s.idf' % (os.path.expanduser(self.games_path), name))
        if len(files) > 0:
            running_name = running_name+'.idf'

        subprocess.Popen('%s -game "%s"%s' % (self.interpreter_command, running_name, self.run_game_command_postfix),
                         shell=True)
        return True

    def delete_game(self, name):
        game_folder_path = os.path.expanduser(self.games_path) + name
        game_idf_path = os.path.expanduser(self.games_path) + name + '.idf'
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
        try:
            info = subprocess.check_output([self.interpreter_command, '-version'])
        except Exception as e:
            return False, e

        if info:
            return True, info.decode('ascii').strip()

    def check_instead_interpreter(self):
        check, info = self.check_instead_interpreter_with_info()
        return check

    @staticmethod
    def size_format(size):
        return InsteadManagerHelper.size_format(size)


class WinInsteadManager(InsteadManager):
    default_config_filename = 'instead-manager-settings-win.json'
    run_game_command_postfix = ''


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


class RepositoryFilesAreMissingError(Exception):
    pass