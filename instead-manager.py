#!/usr/bin/env python

__title__      = 'instead-manager'
__version__    = "0.4"
__author__     = "Evgeniy Efremov"
__email__      = "jhekasoft@gmail.com"

import os
import sys
import platform
import glob
import shutil
import subprocess
import json
import re
import argparse
import urllib.request
from xml.dom import minidom
from packages.colorama import init as coloramaInit, Style


def get_games_from_file(file_path):
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
            print("%s%s%s (%s) %s\n%s%s%s %s [%s]\nDescription URL: %s\nURL: %s\n" % (
                Style.BRIGHT, game['title'], Style.RESET_ALL,
                game['lang'], size_format(int(game['size'])),
                Style.BRIGHT, game['name'], Style.RESET_ALL,
                game['version'],
                game['repository_filename'], game['descurl'], game['url']
            ))
        else:
            print("%s %s%s%s %s" % (
                game['title'],
                Style.BRIGHT, game['name'], Style.RESET_ALL,
                size_format(int(game['size']))
            ))


def get_sorted_local_game_list():
    files = glob.glob('%s*' % os.path.expanduser(games_path))

    local_game_list = []
    for file in files:
        game_name = os.path.basename(file)
        match = re.search('(.*)\.idf$', game_name, re.IGNORECASE)
        if match:
            game_name = match.groups()[0]
        local_game_list.append({'name': game_name})

    local_game_list.sort(key=lambda game: (game['name']))

    return local_game_list


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


def install_action(name: str, run: str, verbose: bool):
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


def local_list_action(verbose: bool):
    local_game_list = get_sorted_local_game_list()
    for local_game in local_game_list:
        print(local_game['name'])


def run_action(name: str):
    running_name = name
    print('Running %s ...' % name)

    # IDF check
    files = glob.glob('%s%s.idf' % (os.path.expanduser(games_path), name))
    if len(files) > 0:
        running_name = running_name+'.idf'

    subprocess.Popen('instead -game %s &>/dev/null' % running_name, shell=True)


def delete_action(name: str):
    game_folder_path = os.path.expanduser(games_path) + name
    game_idf_path = os.path.expanduser(games_path) + name + '.idf'
    if os.path.exists(game_folder_path):
        shutil.rmtree(game_folder_path)
        print("Folder '%s' has been deleted" % game_folder_path)
    elif os.path.exists(game_idf_path):
        os.unlink(game_idf_path)
        print("File '%s' has been deleted" % game_idf_path)
    else:
        print("Folder '%s' doesn't exist. Is name correct?" % game_folder_path)


def is_ansi_output():
    for handle in [sys.stdout, sys.stderr]:
        if (hasattr(handle, "isatty") and handle.isatty()) or ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
            if platform.system()=='Windows' and not ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
                return False
            else:
                return True
        else:
            return False
    return False


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
parser.add_argument('-ansi', '--ansi-output', choices=['on', 'off', 'auto'], nargs='?', const='auto',
                    help='ANSI escaped chars output')

args = parser.parse_args()

# Loading config from JSON-file
jsonSettingsData = open(os.path.dirname(os.path.realpath(__file__))+'/instead-manager-settings.json')
settings = json.load(jsonSettingsData)
repositories = settings['repositories']
games_path = settings['games_path']

# Init colors (colorama)
strip = False
if 'off' == args.ansi_output or ('auto' == args.ansi_output and not is_ansi_output()):
    strip = True

coloramaInit(strip=strip)

if args.update_repositories:
    update_repositories_action()

if args.list:
    list_action(args.verbose)
elif args.search:
    search_action(args.search, args.verbose)
elif args.install:
    install_action(args.install, args.run, args.verbose)
elif args.local_list:
    local_list_action(args.verbose)
elif args.run:
    run_action(args.run)
elif args.delete:
    delete_action(args.delete)
