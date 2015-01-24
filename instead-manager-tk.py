#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__title__ = 'instead-manager'
__version__ = "0.8"
__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
from threading import Thread
from tkinter import *
import tkinter.ttk as ttk
from manager import InsteadManager


class InsteadManagerTk(object):
    installing_game_tree_item = None
    installing_game_title = None

    def __init__(self, instead_manager):
        self.instead_manager = instead_manager

    def begin_repository_downloading_callback(self, repository):
        print('Downloading %s...' % repository['url'])

    def update_repositories_action(self):
        self.instead_manager.\
            update_repositories(begin_repository_downloading_callback=self.begin_repository_downloading_callback)

    def list_action(self):
        game_list = self.instead_manager.get_sorted_game_list()

        local_game_list = self.instead_manager.get_sorted_local_game_list()

        local_game_names = []
        for local_game in local_game_list:
            local_game_names.append(local_game['name'])

        # Clear list
        # map(lambda x: print(x), treeRepositoryList.get_children())
        tree_items = treeRepositoryList.get_children()
        for item in tree_items:
            treeRepositoryList.delete(item)

        # Insert games
        for game in game_list:
            tags = ''
            if game['name'] in local_game_names:
                tags = 'installed'

            treeRepositoryList.insert("", 'end', text=game['name'], values=(
                game['title'], game['lang'], game['version'], self.instead_manager.size_format(int(game['size'])), game['repository_filename']
            ), tags=tags)

    def update_and_list_action(self):
        self.update_repositories_action()
        self.list_action()

    def on_game_list_double_click(self, event):
        item = treeRepositoryList.identify('item', event.x, event.y)
        tags = treeRepositoryList.item(item, "tags")
        name = treeRepositoryList.item(item, "text")
        title = treeRepositoryList.item(item, "values")[0]

        if 'installed' in tags:
            self.instead_manager.run_game(name)
        elif self.installing_game_tree_item is None:
            self.installing_game_tree_item = item
            self.installing_game_title = title

            game_list = self.instead_manager.get_sorted_game_list()
            filtered_game_list = self.instead_manager.filter_games(game_list, name)

            found = bool(filtered_game_list)
            for game in filtered_game_list:

                t = Thread(target=lambda: self.instead_manager.install_game(game,
                                                      download_status_callback=self.download_status_callback,
                                                      begin_installation_callback=self.begin_installation_callback,
                                                      end_installing=self.end_installing))
                t.start()

                break

    def download_status_callback(self, blocknum, blocksize, totalsize):
        loadedsize = blocknum * blocksize
        if loadedsize > totalsize:
            loadedsize = totalsize

        if totalsize > 0:
            percent = loadedsize * 1e2 / totalsize
            s = "%5.1f%% %s / %s" % (
                percent, self.instead_manager.size_format(loadedsize), self.instead_manager.size_format(totalsize))
            treeRepositoryList.set(self.installing_game_tree_item, 'title', '%s %s' % (self.installing_game_title, s))

    def begin_installation_callback(self, game):
        treeRepositoryList.set(self.installing_game_tree_item, 'title', '%s installing...' % self.installing_game_title)

    def end_installing(self, game, result):
        item_index = treeRepositoryList.index(self.installing_game_tree_item)

        self.installing_game_tree_item = None
        self.installing_game_title = None

        self.list_action()

        # Focus installed game
        tree_items = treeRepositoryList.get_children()
        for item in tree_items:
            if treeRepositoryList.index(item) == item_index:
                treeRepositoryList.selection_set(item)
                treeRepositoryList.focus(item)
                treeRepositoryList.yview_scroll(item_index, 'units')
                break


if __name__ == "__main__":
    instead_manager = InsteadManager(os.path.dirname(os.path.realpath(__file__)))
    instead_manager_tk = InsteadManagerTk(instead_manager)

    root = Tk()
    root.wm_title("Instead Manager " + __version__)

    treeRepositoryList = ttk.Treeview(root, columns=('title', 'lang', 'version', 'size', 'repository'), show='headings')
    treeRepositoryList.column("title", width=350)
    treeRepositoryList.column("lang", width=50)
    treeRepositoryList.column("version", width=70)
    treeRepositoryList.column("size", width=70)
    treeRepositoryList.column("repository", width=220)
    treeRepositoryList.heading("title", text="Title")
    treeRepositoryList.heading("lang", text="Lang", command=lambda: print('lang'))
    treeRepositoryList.heading("version", text="Version")
    treeRepositoryList.heading("size", text="Size")
    treeRepositoryList.heading("repository", text="Repository")
    treeRepositoryList.tag_configure('installed', background='#dfd')
    treeRepositoryList.bind("<Double-1>", instead_manager_tk.on_game_list_double_click)
    treeRepositoryList.pack()

    buttonUpdateRepository = ttk.Button(root, text="Update repositories", command=instead_manager_tk.update_and_list_action)
    buttonUpdateRepository.pack()

    # style = ttk.Style()
    # print(style.theme_names())
    # style.theme_use('clam')

    instead_manager_tk.list_action()
    root.mainloop()
