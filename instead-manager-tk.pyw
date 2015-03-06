#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__title__ = 'instead-manager-tk'
__version__ = "0.14"
__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
from threading import Thread
from tkinter import *
import tkinter.ttk as ttk
# import tkinter.font as font
import webbrowser
from manager import InsteadManagerFreeUnix, InsteadManagerWin, InsteadManagerMac, InsteadManagerHelper, RepositoryFilesAreMissingError


class TkMainWindow(object):
    gui_game_list = {}
    gui_selected_item = ''
    gui_messages = {
        'update_repo': 'Update repositories'
    }
    gui_widgets = {}

    def __init__(self, instead_manager, root):
        self.instead_manager = instead_manager
        self.root = root

        self.tk_theme_prepare()

        self.root.resizable(width=FALSE, height=FALSE)

        # Window title
        self.root.title("INSTEAD Manager " + __version__)
        # Window icon
        self.managerLogo = PhotoImage(file=os.path.join(self.instead_manager.base_path, 'resources', 'images', 'logo.gif'))
        self.root.iconphoto(True, self.managerLogo)

        self.content = ttk.Frame(self.root, padding=(5, 5, 5, 5))

        self.tk_filter_prepare()

        self.tk_game_info_prepare()

        # filterImage = PhotoImage(file=os.path.join(base_path, 'resources', 'images', 'icons', 'gnome', 'find.png'))
        # filterButton = ttk.Button(frame, style='Toolbutton', image=filterImage, width=100)
        # filterButton.pack()

        self.tk_games_prepare()

        self.buttonUpdateRepository = ttk.Button(self.content, text=self.gui_messages['update_repo'], command=self.update_and_list_action, width=40)

        self.content.pack(fill='both', expand=True)
        self.frameFilter.grid(column=0, row=0, sticky=(N, S, E, W))
        self.frameGames.grid(column=0, row=1, columnspan=3, rowspan=1, sticky=(N, S, E, W))
        self.frameGameInfo.grid(column=4, row=0, columnspan=3, rowspan=2, sticky=(N, S, E, W))
        self.buttonUpdateRepository.grid(column=0, row=3, sticky=(N, S, E, W))

    def tk_theme_prepare(self):
        pass

    def tk_filter_prepare(self):
        self.frameFilter = ttk.Frame(self.content, borderwidth=0, relief="flat", width=200, height=100)
        self.gui_keyword = StringVar()

        def gui_keyword_change(a, b, c):
            instead_manager_tk.list_action()
            self.entryKeyword.update_idletasks()
        self.gui_keyword.trace('w', gui_keyword_change)

        def gui_repository_change(widget):
            instead_manager_tk.list_action()

        def gui_lang_change(widget):
            instead_manager_tk.list_action()

        self.entryKeyword = ttk.Entry(self.frameFilter, textvariable=self.gui_keyword)
        self.entryKeyword.pack(side=LEFT)

        self.comboboxRepository = ttk.Combobox(self.frameFilter, state="readonly")
        self.comboboxRepository.bind("<<ComboboxSelected>>", gui_repository_change)
        self.comboboxRepository.pack(side=LEFT, padx=5)

        self.comboboxLang = ttk.Combobox(self.frameFilter, state="readonly")
        self.comboboxLang.bind("<<ComboboxSelected>>", gui_lang_change)
        self.comboboxLang.pack(side=LEFT)

        self.gui_only_installed = IntVar()
        def gui_only_installed_change(a, b, c):
            instead_manager_tk.list_action()
            #self.gui_only_installed.update_idletasks()
        self.gui_only_installed.trace('w', gui_only_installed_change)
        self.checkboxOnlyInstalled = ttk.Checkbutton(self.frameFilter, text="Only installed", variable=self.gui_only_installed)
        self.checkboxOnlyInstalled.pack(side=LEFT)

    def tk_game_info_prepare(self):
        self.frameGameInfo = ttk.Frame(self.content, borderwidth=0, relief="flat", width=200, height=100, padding=(5, 0, 0, 0))

        self.managerLogoFrame = ttk.Button(self.frameGameInfo, image=self.managerLogo)
        self.labelGameTitle = ttk.Label(self.frameGameInfo, text='')
        self.labelGameRepository = ttk.Label(self.frameGameInfo, text='')
        self.labelGameVersion = ttk.Label(self.frameGameInfo, text='')
        self.labelGameLang = ttk.Label(self.frameGameInfo, text='')
        self.buttonGamePlay = ttk.Button(self.frameGameInfo, text="Play", command=self.run_game_action)
        self.buttonGameDelete = ttk.Button(self.frameGameInfo, text="Delete", command=self.delete_game_action)
        self.buttonGameInstall = ttk.Button(self.frameGameInfo, text="Install", command=self.install_game_action)
        self.buttonGameOpenInfo = ttk.Button(self.frameGameInfo, text="Info", command=self.game_info_page_open)

        self.managerLogoFrame.pack()
        self.labelGameTitle.pack()
        self.labelGameRepository.pack()
        self.labelGameVersion.pack()
        self.labelGameLang.pack()

    def tk_games_prepare(self):
        self.frameGames = ttk.Frame(self.content, padding=(0, 5, 0, 5))
        self.treeGameList = ttk.Treeview(self.frameGames, columns=('title', 'version', 'size'), selectmode='browse', show='headings', height=14)
        self.treeGameList.column("title", width=350)
        self.treeGameList.column("version", width=70)
        self.treeGameList.column("size", width=70)
        self.treeGameList.heading("title", text="Title")
        self.treeGameList.heading("version", text="Version")
        self.treeGameList.heading("size", text="Size")
        self.treeGameList.tag_configure('installed', background='#f0f0f0')
        self.treeGameList.bind("<Double-1>", self.on_game_list_double_click)
        self.treeGameList.bind('<<TreeviewSelect>>', self.on_game_select)
        self.vsb = ttk.Scrollbar(orient="vertical", command=self.treeGameList.yview)
        self.treeGameList.configure(yscrollcommand=self.vsb.set)
        self.treeGameList.grid(column=0, row=0, sticky=(N, S, E, W))
        self.vsb.grid(column=1, row=0, sticky='ns', in_=self.frameGames)
        self.frameGames.grid_columnconfigure(0, weight=1)
        self.frameGames.grid_rowconfigure(0, weight=1)

    def game_info_page_open(self):
        webbrowser.open_new(self.gui_game_list[self.gui_selected_item]['descurl'])

    def begin_repository_downloading_callback(self, repository):
        self.buttonUpdateRepository['text'] = 'Downloading %s...' % repository['url']

    def end_downloading_repositories(self, list=False):
        self.buttonUpdateRepository['text'] = self.gui_messages['update_repo']
        self.buttonUpdateRepository.state(['!disabled'])
        if list:
            self.list_action()

    def list_action(self):
        try:
            game_list = self.instead_manager.get_sorted_combined_game_list()
        except RepositoryFilesAreMissingError:
            return

        gui_keyboard = self.gui_keyword.get()
        gui_repository = self.comboboxRepository.get()
        gui_lang = self.comboboxLang.get()
        gui_only_installed = self.gui_only_installed.get()

        repositories = [''] + self.instead_manager.get_gamelist_repositories(game_list)
        self.comboboxRepository['values'] = repositories

        langs = [''] + self.instead_manager.get_gamelist_langs(game_list)
        self.comboboxLang['values'] = langs

        if gui_keyboard or gui_repository or gui_lang or gui_only_installed:
            game_list = self.instead_manager.filter_games(game_list, gui_keyboard, gui_repository, gui_lang, gui_only_installed)

        # Clear list
        # map(lambda x: print(x), treeRepositoryList.get_children())
        tree_items = self.treeGameList.get_children()
        for item in tree_items:
            self.treeGameList.delete(item)

        # Insert games
        self.gui_game_list = {}
        for game in game_list:
            game_list_item = game

            tags = ''
            if game_list_item['installed']:
                tags = 'installed'
            item = self.treeGameList.insert("", 'end', text=game_list_item['name'], values=(
                game_list_item['title'],
                game_list_item['version'],
                self.instead_manager.size_format(int(game_list_item['size']))
            ), tags=tags)
            self.gui_game_list[item] = game_list_item

    def update_and_list_action(self):
        self.buttonUpdateRepository.state(['disabled'])
        t = Thread(target=lambda:
                   self.instead_manager.\
                   update_repositories(begin_repository_downloading_callback=self.begin_repository_downloading_callback,
                                       end_downloading_callback=lambda: self.end_downloading_repositories(True)))
        t.start()

    def check_repositories_action(self):
        try:
            self.instead_manager.get_repository_files()
        except RepositoryFilesAreMissingError:
            self.update_and_list_action()
            return
        self.list_action()

    def on_game_list_double_click(self, event):
        #item = treeGameList.identify('item', event.x, event.y)
        item = self.gui_selected_item
        tags = self.treeGameList.item(item, "tags")

        if 'installed' in tags:
            self.run_game_action()
        else:
            self.install_game_action()


    def download_status_callback(self, item, blocknum, blocksize, totalsize):
        loadedsize = blocknum * blocksize
        if loadedsize > totalsize:
            loadedsize = totalsize

        if totalsize > 0:
            percent = loadedsize * 1e2 / totalsize
            s = "%5.1f%% %s / %s" % (
                percent, self.instead_manager.size_format(loadedsize), self.instead_manager.size_format(totalsize))
            self.treeGameList.set(item, 'title', '%s %s' % (self.gui_game_list[item]['title'], s))

    def begin_installation_callback(self, item):
        self.treeGameList.set(item, 'title', '%s installing...' % self.gui_game_list[item]['title'])

    def end_installation(self, item, game, result):
        item_index = self.treeGameList.index(item)

        self.list_action()

        # Focus installed game
        tree_items = self.treeGameList.get_children()
        for item in tree_items:
            if self.treeGameList.index(item) == item_index:
                self.treeGameList.focus(item)
                self.treeGameList.selection_set(item)
                self.treeGameList.yview_scroll(item_index, 'units')
                break

    def on_game_select(self, event):
        self.gui_selected_item = self.treeGameList.focus()
        title = self.gui_game_list[self.gui_selected_item]['title']
        repository = self.gui_game_list[self.gui_selected_item]['repository_filename']
        version = self.gui_game_list[self.gui_selected_item]['version']
        lang = self.gui_game_list[self.gui_selected_item]['lang']
        self.labelGameTitle.config(text=title)
        self.labelGameRepository.config(text=repository)
        self.labelGameVersion.config(text=version)
        self.labelGameLang.config(text=lang)
        self.change_game_buttons_state(self.gui_game_list[self.gui_selected_item]['installed'],
                                       True if self.gui_game_list[self.gui_selected_item]['descurl'] else False)

    def install_game_action(self):
        item = self.gui_selected_item

        game = self.gui_game_list[item]

        t = Thread(target=lambda:
            self.instead_manager.install_game(game,
                                              download_status_callback=lambda blocknum, blocksize, totalsize: self.download_status_callback(item, blocknum, blocksize, totalsize),
                                              begin_installation_callback=lambda game: self.begin_installation_callback(item),
                                              end_installation=lambda game, result: self.end_installation(item, game, result)))
        t.start()

    def run_game_action(self):
        item = self.gui_selected_item
        name = self.treeGameList.item(item, "text")
        self.instead_manager.run_game(name)

    def delete_game_action(self):
        item = self.gui_selected_item
        name = self.treeGameList.item(item, "text")
        self.instead_manager.delete_game(name)
        self.list_action()

    def change_game_buttons_state(self, installed, desc_url_exists=False):
        self.buttonGameOpenInfo.pack_forget()

        if installed:
            self.buttonGamePlay.pack()
            self.buttonGameDelete.pack()
            self.buttonGameInstall.pack_forget()
        else:
            self.buttonGamePlay.pack_forget()
            self.buttonGameDelete.pack_forget()
            self.buttonGameInstall.pack()

        if desc_url_exists:
            self.buttonGameOpenInfo.pack()


class TkMainWindowFreeUnix(TkMainWindow):
    def tk_theme_prepare(self):
        # ttk theme for UNIX-like systems
        import packages.ttk_themes.plastik.plastik_theme as plastik_theme
        try:
            plastik_theme.install(os.path.join(self.instead_manager.base_path, 'packages', 'ttk_themes', 'plastik', 'plastik'))
        except Exception as e:
            import warnings
            warnings.warn("plastik theme being used without images")


if __name__ == "__main__":
    try:
        base_path = os.path.dirname(os.path.realpath(__file__))
    except NameError:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    root = Tk(className='INSTEAD Manager')

    if InsteadManagerHelper.is_win():
        instead_manager = InsteadManagerWin(base_path)
        instead_manager_tk = TkMainWindow(instead_manager, root)
    elif InsteadManagerHelper.is_mac():
        instead_manager = InsteadManagerMac(base_path)
        instead_manager_tk = TkMainWindow(instead_manager, root)
    elif InsteadManagerHelper.is_free_unix():
        instead_manager = InsteadManagerFreeUnix(base_path)
        instead_manager_tk = TkMainWindowFreeUnix(instead_manager, root)
    else:
        instead_manager = InsteadManagerFreeUnix(base_path)
        instead_manager_tk = TkMainWindow(instead_manager, root)

    root.wait_visibility()
    instead_manager_tk.check_repositories_action()
    root.mainloop()
