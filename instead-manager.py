#!/usr/bin/env python

__author__     = "Evgeniy Efremov"
__version__    = "0.2"
__email__      = "jhekasoft@gmail.com"

#import time
import sys
import os
import glob
import shutil
import subprocess
#import signal
#import logging
import json
import re
import argparse
import urllib.request
from xml.dom import minidom


def get_games_from_file(file_path):
    xml_doc = minidom.parse(file_path)
    xml_game_list = xml_doc.getElementsByTagName('game')

    repository_filename = os.path.basename(file_path);

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


def get_sorted_game_list():
    files = glob.glob('%s/repositories/*.xml' % os.path.dirname(os.path.realpath(__file__)));

    game_list = []
    for file in files:
        game_list.extend(get_games_from_file(file))

    game_list.sort(key=lambda game: (game['title']))

    return game_list


def print_game_list(game_list: int, verbose: bool):
    for game in game_list:
        if verbose:
            print("\033[1m%s\033[0m (%s) %s\n\033[1m%s\033[0m %s [%s]\nDescription URL: %s\nURL: %s\n" % (
                game['title'], game['lang'], size_format(int(game['size'])), game['name'], game['version'],
                game['repository_filename'], game['descurl'], game['url']
            ))
        else:
            print("%s \033[1m%s\033[0m %s" % (
                game['title'], game['name'], size_format(int(game['size']))
            ))


def size_format(size):
    suffix = 'B'
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size) < 1024.0:
            return "%3.1f%s%s" % (size, unit, suffix)
        size /= 1024.0
    return "%.1f%s%s" % (size, 'Yi', suffix)


def get_response_filename(http_message, url):
    filename = None

    content_disposition = http_message.get('Content-Disposition')
    if content_disposition:
        filename = re.findall("filename=(\S+)", content_disposition)[0].strip(' \t\n\r"\'')

    if not filename:
        filename = url.split('/')[-1]

    return filename


def update_repositories_action():
    print('Updating repositories...')

    for repository in repositories:
        print('Downloading %s ...' % repository['url'])
        filename = '%s/repositories/%s.xml' % (os.path.dirname(os.path.realpath(__file__)), repository['name'])
        urllib.request.urlretrieve(repository['url'], filename)


def list_action(verbose: bool):
    game_list = get_sorted_game_list()
    print_game_list(game_list, verbose)


def search_action(search: str, verbose: bool):
    game_list = get_sorted_game_list()

    filtered_game_list = []
    search_regex = '.*%s.*' % re.escape(search)
    for game in game_list:
        if re.search(search_regex, game['title'], re.IGNORECASE) or re.search(search_regex, game['name'], re.IGNORECASE):
            filtered_game_list.append(game)

    print_game_list(filtered_game_list, verbose)


def install_action(name: str, run: bool, verbose: bool):
    game_list = get_sorted_game_list()

    search_regex = '.*%s.*' % re.escape(name)
    for game in game_list:
        if re.search(search_regex, game['title'], re.IGNORECASE) or re.search(search_regex, game['name'], re.IGNORECASE):
            # Downloading game to the temp file
            print('Downloading %s ...' % game['url'])
            tmp_game_path = '%s/games/' % os.path.dirname(os.path.realpath(__file__))
            game_tmp_filename = '%s%s' % (tmp_game_path, 'tmp_'+game['name']+'.part')
            result = urllib.request.urlretrieve(game['url'], game_tmp_filename)

            base_game_filename = get_response_filename(result[1], game['url']);
            game_filename = '%s%s' % (tmp_game_path, base_game_filename)

            # Copying game to the file with normal name
            shutil.copy(game_tmp_filename, game_filename)
            os.remove(game_tmp_filename)

            # Installing game
            print('%s \033[1m%s\033[0m %s installing...' % (game['title'], game['name'], game['version']))
            # Quit after installing or run game
            quit = ' -quit'
            if run:
                quit = ''
            return_code = subprocess.call('instead -install %s%s' % (game_filename, quit), shell=True)

            if 0 == return_code:
                print('Compete')

            os.remove(game_filename)
            break

parser = argparse.ArgumentParser(description='INSTEAD games manager %s' % __version__)
parser.add_argument('-u', '--update-repositories', action='store_true',
                   help='update repositories')
parser.add_argument('-l', '--list', action='store_true',
                   help='list games')
parser.add_argument('-s', '--search', nargs='?', type=str,
                   help='search games')
parser.add_argument('-i', '--install', nargs='?', type=str,
                   help='install game by name or title')
parser.add_argument('-r', '--run', action='store_true',
                   help='run game after installation')
parser.add_argument('-v', '--verbose', action='store_true',
                   help='detailed print')

args = parser.parse_args()

# Loading config from JSON-file
jsonSettingsData = open(os.path.dirname(os.path.realpath(__file__))+'/instead-manager-settings.json')
settings = json.load(jsonSettingsData)
repositories = settings['repositories']

if args.update_repositories:
    update_repositories_action()

if args.list:
    list_action(args.verbose)
elif args.search:
    search_action(args.search, args.verbose)
elif args.install:
    install_action(args.install, args.run, args.verbose)
