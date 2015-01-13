__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
import sys
import platform
import glob
import subprocess
from xml.dom import minidom
import re
from packages.colorama import Style


class InsteadManager(object):

    def __init__(self, games_path, base_path, interpreter_command, repositories):
        self.games_path = games_path
        self.base_path = base_path
        self.interpreter_command = interpreter_command
        self.repositories = repositories

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
