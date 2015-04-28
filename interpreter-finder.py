__author__ = 'jhekasoft'

import os
import sys
import re
import subprocess
from abc import ABCMeta, abstractmethod


class InsteadInterpreterFinder(object, metaclass=ABCMeta):

    download_link = 'http://instead.syscall.ru/ru/download/'

    def __init__(self):
        pass

    def find_interpreter(self):
        for path in self.exact_file_paths:
            if self.check_interpreter_path(path):
                return path

        return None

    def check_interpreter_path(self, path: str):
        return os.path.exists(path)

    def get_download_link(self):
        return self.download_link

    def get_interpreter_version(self, interpreter_command: str):
        try:
            info = subprocess.check_output([interpreter_command, '-version'])
        except Exception as e:
            return False, e

        if info:
            return True, info.decode('ascii').strip()


class InsteadInterpreterFinderFreeUnix(InsteadInterpreterFinder):

    def find_interpreter(self):
        interpreter_command = "instead"
        if 0 == subprocess.call(["which", interpreter_command], stdout=subprocess.PIPE):
            return interpreter_command

        return None


class InsteadInterpreterFinderMac(InsteadInterpreterFinder):

    exact_file_paths = [
        '/Applications/Instead.app/Contents/MacOS/sdl-instead'
    ]


class InsteadInterpreterFinderWin(InsteadInterpreterFinder):

    exact_file_paths = []

    def __init__(self):
        drives = re.findall(r"[A-Z]+:.*$", os.popen("mountvol /").read(), re.MULTILINE)
        for drive in drives:
            self.exact_file_paths.append(drive + 'Program Files\Games\INSTEAD\sdl-instead.exe')
            self.exact_file_paths.append(drive + 'Program Files (x86)\Games\INSTEAD\sdl-instead.exe')


if __name__ == "__main__":
    interpreter_finder = InsteadInterpreterFinderMac()
    interpreter_path = interpreter_finder.find_interpreter()
    print(interpreter_path)
    if interpreter_path:
        print(interpreter_finder.get_interpreter_version(interpreter_path))
