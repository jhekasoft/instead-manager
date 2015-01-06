#!/usr/bin/env python

#import time
#import sys
import os
import glob
#import signal
#import logging
#import json
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
        game_list_unsorted.append({
            'title': title.firstChild.data,
            'name': name.firstChild.data,
            'version': version.firstChild.data,
            'lang': lang.firstChild.data,
            'url': url.firstChild.data,
            'size': size.firstChild.data,
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
            print("\033[1m%s\033[0m (%s) %s\n\033[1m%s\033[0m %s [%s]\n" % (
                game['title'], game['lang'], size_format(int(game['size'])), game['name'], game['version'], game['repository_filename']
            ))
        else:
            print("%s \033[1m%s\033[0m" % (
                game['title'], game['name']
            ))


def size_format(size):
    suffix = 'B'
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size) < 1024.0:
            return "%3.1f%s%s" % (size, unit, suffix)
        size /= 1024.0
    return "%.1f%s%s" % (size, 'Yi', suffix)


def update_repositories_action():
    print('Updating repositories...')
    repositories = [
        {'name': 'official', 'url': 'http://instead-launcher.googlecode.com/svn/pool/game_list.xml'},
        {'name': 'instead-games', 'url': 'http://instead-games.ru/xml.php'},
        {'name': 'instead-games-sandbox', 'url': 'http://instead-games.ru/xml2.php'},
    ]

    for repository in repositories:
        print('Downloading %s' % repository['url'])
        filename = '%s/repositories/%s.xml' % (os.path.dirname(os.path.realpath(__file__)), repository['name']);
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


parser = argparse.ArgumentParser(description='INSTEAD games manager.')
parser.add_argument('-u', '--update-repositories', action='store_true',
                   help='update repositories')
parser.add_argument('-l', '--list', action='store_true',
                   help='list games')
parser.add_argument('-s', '--search', nargs='?', type=str,
                   help='search games')
parser.add_argument('-v', '--verbose', action='store_true',
                   help='detailed print')

args = parser.parse_args()

if args.update_repositories:
    update_repositories_action()

if args.list:
    list_action(args.verbose)
elif args.search:
    search_action(args.search, args.verbose)
