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

    def __init__(self, base_path, games_path=None, interpreter_command=None, repositories=None):
        self.base_path = base_path

        if None in (games_path, interpreter_command, repositories):
            settings = self.read_settings()

        self.games_path = games_path if games_path else settings['games_path']
        self.interpreter_command = interpreter_command if interpreter_command else settings['interpreter_command']
        self.repositories = repositories if repositories else settings['repositories']

    def read_settings(self):
        """
        Loading config from JSON-file

        :return:
        """
        config_file = 'instead-manager-settings.json'
        if self.is_win():
            config_file = 'instead-manager-settings-win.json'

        json_settings_data = open(os.path.join(self.base_path, config_file))

        return json.load(json_settings_data)

    def get_sorted_game_list(self):
        files = glob.glob('%s/repositories/*.xml' % self.base_path)

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

    def filter_games(self, game_list, keyword: str):
        filtered_game_list = []
        search_regex = '.*%s.*' % re.escape(keyword)
        for game in game_list:
            if re.search(search_regex, game['title'], re.IGNORECASE) or re.search(search_regex, game['name'], re.IGNORECASE):
                filtered_game_list.append(game)

        return filtered_game_list

    def update_repositories(self, download_status_callback=None, begin_repository_downloading_callback=None):
        for repository in self.repositories:
            if begin_repository_downloading_callback:
                begin_repository_downloading_callback(repository)

            filename = os.path.join(self.base_path, 'repositories', repository['name']+'.xml')
            urllib.request.urlretrieve(repository['url'], filename, download_status_callback)

        return True

    def install_game(self, game, run: bool, download_status_callback=None,
                     begin_downloading_callback=None, begin_installation_callback=None):

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

        if 0 != return_code:
            return False

        return True

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

        postfix = ''
        if not InsteadManager.is_win():
            postfix = ' &>/dev/null'
        subprocess.Popen('%s -game "%s"%s' % (self.interpreter_command, running_name, postfix), shell=True)
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
