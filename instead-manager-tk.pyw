#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__title__ = 'instead-manager-tk'
__author__ = "Evgeniy Efremov aka jhekasoft"
__email__ = "jhekasoft@gmail.com"

import os
from threading import Thread
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
# import tkinter.font as font
import webbrowser
from packages.instead_manager.manager import InsteadManager, InsteadManagerFreeUnix, InsteadManagerWin, InsteadManagerMac, InsteadManagerHelper, RepositoryFilesAreMissingError
from packages.instead_manager.interpreter_finder import InsteadInterpreterFinderFreeUnix, InsteadInterpreterFinderWin, InsteadInterpreterFinderMac


class TkMainWindow(object):
    gui_game_list = {}
    gui_selected_item = ''
    gui_installed_game_index = None
    gui_messages = {
        'update_repo': 'Update',
        'settings': 'Settings',
        'test': 'Test',
    }
    gui_widgets = {}
    gui_frame_game_info_show = True
    gui_frame_filter_show = True
    is_games_need_update = False

    def __init__(self, instead_manager: InsteadManager, root: Tk):
        self.instead_manager = instead_manager
        self.root = root

        self.tk_theme_prepare()

        self.root.resizable(width=FALSE, height=FALSE)

        # Window title
        self.root.title("INSTEAD Manager " + self.instead_manager.version)
        # Window icon
        self.managerLogo = PhotoImage(file=os.path.join(self.instead_manager.base_path, 'resources', 'images', 'logo.gif'))
        self.root.iconphoto(True, self.managerLogo)

        self.content = ttk.Frame(self.root, padding=(5, 5, 5, 5))

        self.tk_toolbar_prepare()

        self.tk_filter_prepare()

        self.tk_game_info_prepare()

        self.tk_games_prepare()

        self.content.pack(fill=BOTH, expand=True)
        self.frameToolbar.grid(column=0, row=0, columnspan=3, sticky=(N, S, E, W))
        self.frameGames.grid(column=0, row=2, columnspan=3, rowspan=1, sticky=(N, S, E, W))
        self.tk_filter_toggle()
        self.tk_game_info_toggle()
        # self.buttonUpdateRepository.grid(column=0, row=4, sticky=(N, S, E, W))

    def tk_theme_prepare(self):
        pass

    def tk_game_info_toggle(self):
        if self.gui_frame_game_info_show:
            self.frameGameInfo.grid(column=4, row=0, columnspan=3, rowspan=3, sticky=(N, S, E, W))
        else:
            self.frameGameInfo.grid_forget()

        self.gui_frame_game_info_show = not self.gui_frame_game_info_show

    def tk_filter_toggle(self):
        if self.gui_frame_filter_show:
            self.frameFilter.grid(column=0, row=1, columnspan=3, sticky=(N, S, E, W))
        else:
            self.frameFilter.grid_forget()

        self.gui_frame_filter_show = not self.gui_frame_filter_show

    def tk_open_settings_window(self):
        TkSettingsWindow(self, self.instead_manager)

    def tk_toolbar_prepare(self):
        self.frameToolbar = ttk.Frame(self.content, borderwidth=0, relief="flat", width=200, height=100)

        self.iconUpdate = PhotoImage(file=os.path.join(self.instead_manager.base_path, 'resources', 'images', 'icons', 'update.gif'))
        self.buttonUpdateRepository = ttk.Button(self.frameToolbar, style='Toolbutton', text=self.gui_messages['update_repo'], image=self.iconUpdate, compound=LEFT, command=self.update_and_list_action)
        self.buttonUpdateRepository.pack(side=LEFT)

        self.iconInfo = PhotoImage(file=os.path.join(self.instead_manager.base_path, 'resources', 'images', 'icons', 'info.gif'))
        self.buttonToggleGameInfo = ttk.Button(self.frameToolbar, style='Toolbutton', text="Info", image=self.iconInfo, compound=LEFT, command=self.tk_game_info_toggle)
        self.buttonToggleGameInfo.pack(side=RIGHT)

        self.iconFilter = PhotoImage(file=os.path.join(self.instead_manager.base_path, 'resources', 'images', 'icons', 'filter.gif'))
        self.buttonToggleFilter = ttk.Button(self.frameToolbar, style='Toolbutton', text="Filter", image=self.iconFilter, compound=LEFT, command=self.tk_filter_toggle)
        self.buttonToggleFilter.pack(side=RIGHT)

        self.iconSettings = PhotoImage(file=os.path.join(self.instead_manager.base_path, 'resources', 'images', 'icons', 'settings.gif'))
        self.buttonShowSettings = ttk.Button(self.frameToolbar, style='Toolbutton', text=self.gui_messages['settings'], compound=LEFT, image=self.iconSettings, command=self.tk_open_settings_window)
        self.buttonShowSettings.pack(side=RIGHT)

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

        self.labelKeyword = ttk.Label(self.frameFilter, text="Search:")
        self.entryKeyword = ttk.Entry(self.frameFilter, textvariable=self.gui_keyword, width=10)
        self.labelKeyword.pack(side=LEFT)
        self.entryKeyword.pack(side=LEFT)

        self.labelRepository = ttk.Label(self.frameFilter, text="Repo:")
        self.comboboxRepository = ttk.Combobox(self.frameFilter, state="readonly", width=16)
        self.comboboxRepository.bind("<<ComboboxSelected>>", gui_repository_change)
        self.labelRepository.pack(side=LEFT)
        self.comboboxRepository.pack(side=LEFT, padx=5)

        self.labelLang = ttk.Label(self.frameFilter, text="Lang:")
        self.comboboxLang = ttk.Combobox(self.frameFilter, state="readonly", width=3)
        self.comboboxLang.bind("<<ComboboxSelected>>", gui_lang_change)
        self.labelLang.pack(side=LEFT)
        self.comboboxLang.pack(side=LEFT)

        self.gui_only_installed = IntVar()

        def gui_only_installed_change(a, b, c):
            instead_manager_tk.list_action()
            # self.gui_only_installed.update_idletasks()

        self.gui_only_installed.trace('w', gui_only_installed_change)
        self.checkboxOnlyInstalled = ttk.Checkbutton(self.frameFilter, text="Only installed", variable=self.gui_only_installed)
        self.checkboxOnlyInstalled.pack(side=LEFT)

    def tk_game_info_prepare(self):
        self.frameGameInfo = ttk.Frame(self.content, borderwidth=0, relief="flat", width=200, height=100, padding=(5, 0, 0, 0))

        self.managerLogoFrame = ttk.Label(self.frameGameInfo, image=self.managerLogo, padding=(15, 0, 15, 0))
        self.labelGameTitle = ttk.Label(self.frameGameInfo, text='', font="-weight bold")
        self.labelGameRepository = ttk.Label(self.frameGameInfo, text='')
        self.labelGameVersion = ttk.Label(self.frameGameInfo, text='')
        self.labelGameLang = ttk.Label(self.frameGameInfo, text='')
        self.buttonGamePlay = ttk.Button(self.frameGameInfo, text="Play", command=self.run_game_action)
        self.buttonGameDelete = ttk.Button(self.frameGameInfo, text="Delete", command=self.delete_game_action)
        self.buttonGameInstall = ttk.Button(self.frameGameInfo, text="Install", command=self.install_game_action)
        self.buttonGameOpenInfo = ttk.Button(self.frameGameInfo, text="Details", command=self.game_info_page_open)

        self.managerLogoFrame.pack()
        self.labelGameTitle.pack()
        self.labelGameRepository.pack()
        self.labelGameVersion.pack()
        self.labelGameLang.pack()

    def tk_games_prepare(self):
        self.frameGames = ttk.Frame(self.content, padding=(0, 5, 0, 5))
        self.treeGameList = ttk.Treeview(self.frameGames, columns=('title', 'version', 'size'), selectmode='browse', show='headings', height=18)
        self.treeGameList.column("title", width=400)
        self.treeGameList.column("version", width=70)
        self.treeGameList.column("size", width=70)
        self.treeGameList.heading("title", text="Title")
        self.treeGameList.heading("version", text="Version")
        self.treeGameList.heading("size", text="Size")
        self.treeGameList.tag_configure('installed', background='#f0f0f0')
        self.treeGameList.bind('<<TreeviewSelect>>', self.on_game_select)
        self.treeGameList.bind("<Double-1>", self.on_game_list_double_click)
        self.vsb = ttk.Scrollbar(orient="vertical", command=self.treeGameList.yview)
        self.treeGameList.configure(yscrollcommand=self.vsb.set)
        self.treeGameList.grid(column=0, row=0, sticky=(N, S, E, W))
        self.vsb.grid(column=1, row=0, sticky='ns', in_=self.frameGames)
        self.frameGames.grid_columnconfigure(0, weight=1)
        self.frameGames.grid_rowconfigure(0, weight=1)

    def game_info_page_open(self):
        webbrowser.open_new(self.gui_game_list[self.gui_selected_item]['descurl'])

    def begin_repository_downloading_callback(self, repository):
        self.buttonUpdateRepository['text'] = 'Updating...'

    def end_downloading_repositories(self, list=False):
        self.buttonUpdateRepository['text'] = self.gui_messages['update_repo']
        self.buttonUpdateRepository['image'] = self.iconUpdate
        self.buttonUpdateRepository.state(['!disabled'])
        if list:
            self.is_games_need_update = True;
            # self.list_action()

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
            self.gui_game_list[item]['installing'] = False

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
            percent = loadedsize * 100 / totalsize
            s = "%5.1d%% %s / %s" % (
                percent, self.instead_manager.size_format(loadedsize), self.instead_manager.size_format(totalsize))
            self.treeGameList.set(item, 'title', '%s %s' % (self.gui_game_list[item]['title'], s))

    def begin_installation_callback(self, item):
        self.treeGameList.set(item, 'title', '%s installing...' % self.gui_game_list[item]['title'])

    def end_installation(self, item, game, result):
        self.gui_game_list[item]['installing'] = False
        self.gui_installed_game_index = self.treeGameList.index(item)

        # Check if another games are installing
        for gui_game in self.gui_game_list:
            if self.gui_game_list[gui_game]['installing']:
                return

        # Update game list if the all games is installed
        self.is_games_need_update = True

    def check_game_list_update(self):
        if self.is_games_need_update:
            self.list_action()
            self.is_games_need_update = False

            # Focus installed game
            if self.gui_installed_game_index is not None:
                self.focus_game(self.gui_installed_game_index)
                self.gui_installed_game_index = None

        self.root.after(100, self.check_game_list_update)

    def focus_game(self, item_index):
        tree_items = self.treeGameList.get_children()
        for item in tree_items:
            if self.treeGameList.index(item) == item_index:
                self.treeGameList.focus(item)
                self.treeGameList.selection_set(item)
                # self.treeGameList.yview_scroll(item_index, 'units')
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
        self.gui_game_list[item]['installing'] = True

    def run_game_action(self):
        item = self.gui_selected_item
        name = self.treeGameList.item(item, "text")
        if not self.instead_manager.run_game(name):
            messagebox.showerror("Running failed", "Running failed. Please check your INSTEAD command in the settings.")

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


class TkSettingsWindow(object):

    def __init__(self, main_window: TkMainWindow, instead_manager: InsteadManager):
        self.main_window = main_window
        self.instead_manager = instead_manager
        self.slave = Toplevel(main_window.root)
        self.slave.title('Settings')
        # self.slave.geometry('200x150+400+300')
        self.slave.resizable(width=FALSE, height=FALSE)

        self.gui_interpreter_command = StringVar()
        self.content = ttk.Frame(self.slave, padding=(5, 5, 5, 5))
        self.content.pack()

        self.contentInterpreterCommand = ttk.Frame(self.content)
        self.contentInterpreterCommand.pack()

        self.labelCommand = ttk.Label(self.contentInterpreterCommand, text="INSTEAD command:")
        self.entryCommand = ttk.Entry(self.contentInterpreterCommand, textvariable=self.gui_interpreter_command, width=50)
        self.buttonSelectInterpreter = ttk.Button(self.contentInterpreterCommand, text="...", width=3, style='Toolbutton', command=self.select_interpreter)
        self.buttonFindInterpreter = ttk.Button(self.contentInterpreterCommand, text="Detect", command=self.find_interpreter)
        self.buttonTestInterpreter = ttk.Button(self.contentInterpreterCommand, text=self.main_window.gui_messages["test"], command=self.test_interpreter)
        self.labelCommand.pack(side=LEFT)
        self.entryCommand.pack(side=LEFT)
        self.buttonSelectInterpreter.pack(side=LEFT)
        self.buttonFindInterpreter.pack(side=LEFT)
        self.buttonTestInterpreter.pack(side=LEFT)

        self.contentButtons = ttk.Frame(self.content, padding=(0, 15, 0, 0))
        self.contentButtons.pack()
        self.buttonSave = ttk.Button(self.contentButtons, text="Save", command=self.save)
        self.buttonCancel = ttk.Button(self.contentButtons, text="Cancel", command=self.cancel)
        self.buttonSave.pack(side=LEFT)
        self.buttonCancel.pack(side=LEFT)

        settings = self.instead_manager.read_settings()
        self.gui_interpreter_command.set(settings["interpreter_command"])

        self.slave.grab_set()
        self.slave.focus_set()
        self.slave.wait_window()

    def save(self):
        settings = self.instead_manager.read_settings()
        settings["interpreter_command"] = self.gui_interpreter_command.get()
        self.instead_manager.save_settings(settings)
        self.instead_manager.reload_settings()
        self.slave.destroy()

    def cancel(self):
        self.slave.destroy()

    def select_interpreter(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.gui_interpreter_command.set(filename)

    def find_interpreter(self):
        interpreter_command = self.instead_manager.interpreter_finder.find_interpreter()
        if interpreter_command:
            self.gui_interpreter_command.set(interpreter_command)

    def test_interpreter(self):
        self.main_window.root.update_idletasks()
        check, info = self.instead_manager.check_instead_interpreter_with_info(self.gui_interpreter_command.get())
        if check:
            messagebox.showinfo("INSTEAD is OK", "There is INSTEAD " + info + ".")
        else:
            messagebox.showerror("Running failed", "INSTEAD running failed.")

if __name__ == "__main__":
    try:
        base_path = os.path.dirname(os.path.realpath(__file__))
    except NameError:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    root = Tk(className='INSTEAD Manager')

    if InsteadManagerHelper.is_win():
        instead_manager = InsteadManagerWin(base_path, InsteadInterpreterFinderWin())
        instead_manager_tk = TkMainWindow(instead_manager, root)
    elif InsteadManagerHelper.is_mac():
        instead_manager = InsteadManagerMac(base_path, InsteadInterpreterFinderMac())
        instead_manager_tk = TkMainWindow(instead_manager, root)
    elif InsteadManagerHelper.is_free_unix():
        instead_manager = InsteadManagerFreeUnix(base_path, InsteadInterpreterFinderFreeUnix())
        instead_manager_tk = TkMainWindowFreeUnix(instead_manager, root)
    else:
        instead_manager = InsteadManagerFreeUnix(base_path)
        instead_manager_tk = TkMainWindow(instead_manager, root)

    root.wait_visibility()
    instead_manager_tk.check_repositories_action()
    instead_manager_tk.check_game_list_update()
    root.mainloop()
