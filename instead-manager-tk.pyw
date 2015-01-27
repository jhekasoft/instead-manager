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
from manager import InsteadManager, WinInsteadManager, InsteadManagerHelper


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
        tree_items = treeGameList.get_children()
        for item in tree_items:
            treeGameList.delete(item)

        # Insert games
        for game in game_list:
            tags = ''
            if game['name'] in local_game_names:
                tags = 'installed'

            treeGameList.insert("", 'end', text=game['name'], values=(
                game['title'], game['lang'], game['version'], self.instead_manager.size_format(int(game['size'])), game['repository_filename']
            ), tags=tags)

    def update_and_list_action(self):
        self.update_repositories_action()
        self.list_action()

    def on_game_list_double_click(self, event):
        item = treeGameList.identify('item', event.x, event.y)
        tags = treeGameList.item(item, "tags")
        name = treeGameList.item(item, "text")
        title = treeGameList.item(item, "values")[0]

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
            treeGameList.set(self.installing_game_tree_item, 'title', '%s %s' % (self.installing_game_title, s))

    def begin_installation_callback(self, game):
        treeGameList.set(self.installing_game_tree_item, 'title', '%s installing...' % self.installing_game_title)

    def end_installing(self, game, result):
        item_index = treeGameList.index(self.installing_game_tree_item)

        self.installing_game_tree_item = None
        self.installing_game_title = None

        self.list_action()

        # Focus installed game
        tree_items = treeGameList.get_children()
        for item in tree_items:
            if treeGameList.index(item) == item_index:
                treeGameList.selection_set(item)
                treeGameList.focus(item)
                treeGameList.yview_scroll(item_index, 'units')
                break

    def on_game_select(self, event):
        title = treeGameList.item(treeGameList.focus(), "values")[0]
        label.config(text=title)


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.realpath(__file__))

    if InsteadManagerHelper.is_win():
        instead_manager = WinInsteadManager(base_path)
    else:
        instead_manager = InsteadManager(base_path)

    instead_manager_tk = InsteadManagerTk(instead_manager)

    root = Tk(className='INSTEAD Manager')
    # Window title
    root.title("INSTEAD Manager " + __version__)
    # Window icon
    root.iconphoto(True, PhotoImage(file=os.path.join(base_path, 'resources', 'images', 'logo.png')))

    # style = ttk.Style()
    # print(style.theme_names())
    # style.theme_use('clam')

    content = ttk.Frame(root)
    frame = ttk.Frame(content, borderwidth=5, relief="sunken", width=200, height=100)
    label = ttk.Label(frame, text='')
    label.pack()

    treeGameList = ttk.Treeview(content, columns=('title', 'lang', 'version', 'size', 'repository'), show='headings')
    treeGameList.column("title", width=350)
    treeGameList.column("lang", width=50)
    treeGameList.column("version", width=70)
    treeGameList.column("size", width=70)
    treeGameList.column("repository", width=220)
    treeGameList.heading("title", text="Title")
    treeGameList.heading("lang", text="Lang", command=lambda: print('lang'))
    treeGameList.heading("version", text="Version")
    treeGameList.heading("size", text="Size")
    treeGameList.heading("repository", text="Repository")
    treeGameList.tag_configure('installed', background='#dfd')
    treeGameList.bind("<Double-1>", instead_manager_tk.on_game_list_double_click)
    treeGameList.bind('<<TreeviewSelect>>', instead_manager_tk.on_game_select)
    # treeGameList.pack()

    buttonUpdateRepository = ttk.Button(content, text="Update repositories", command=instead_manager_tk.update_and_list_action)

    content.grid(column=0, row=0)
    treeGameList.grid(column=0, row=0, columnspan=3, rowspan=2)
    frame.grid(column=4, row=0, columnspan=3, rowspan=2)
    buttonUpdateRepository.grid(column=0, row=3)

    # Style Sheet
    # s = ttk.Style()
    # s.configure('TFrame', background='#5555ff')
    # s.configure('TButton', background='blue', foreground='#eeeeff', font=('Sans', '14', 'bold'), sticky=EW)
    # s.configure('TLabel', font=('Sans', '16', 'bold'), background='#5555ff', foreground='#eeeeff')
    # s.map('TButton', foreground=[('hover', '#5555ff'), ('focus', 'yellow')])
    # s.map('TButton', background=[('hover', '#eeeeff'), ('focus', 'orange')])
    # s.configure('TCombobox', background='#5555ff', foreground='#3333ff', font=('Sans', 18))

    #buttonUpdateRepository.pack()

    instead_manager_tk.list_action()
    root.mainloop()
