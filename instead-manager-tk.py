#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__title__ = 'instead-manager'
__version__ = "0.8"
__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
from tkinter import *
import tkinter.ttk as ttk
from manager import InsteadManager


class InsteadManagerTk(object):

    def __init__(self, instead_manager):
        self.instead_manager = instead_manager

    def begin_repository_downloading_callback(self, repository):
        print('Downloading %s...' % repository['url'])

    def update_repositories_action(self):
        self.instead_manager.\
            update_repositories(begin_repository_downloading_callback=self.begin_repository_downloading_callback)

    def list_action(self):
        game_list = self.instead_manager.get_sorted_game_list()
        for game in game_list:
            print(game['name'] + ' ' + game['version'])
            treeRepositoryList.insert("", 'end', text=game['title'], values=(game['name'], game['version']))


if __name__ == "__main__":
    instead_manager = InsteadManager(os.path.dirname(os.path.realpath(__file__)))
    instead_manager_tk = InsteadManagerTk(instead_manager)

    root = Tk()

    buttonUpdateRepository = ttk.Button(root, text="Update repositories", command=instead_manager_tk.update_repositories_action)
    buttonUpdateRepository.pack()

    buttonList = ttk.Button(root, text="List all games", command=instead_manager_tk.list_action)
    buttonList.pack()

    treeRepositoryList = ttk.Treeview(root, columns=('name', 'version'))
    treeRepositoryList.heading("name", text="Name")
    treeRepositoryList.heading("version", text="Version")
    treeRepositoryList.pack()

    root.mainloop()
