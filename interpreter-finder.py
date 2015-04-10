__author__ = 'jheka'

import os
from abc import ABCMeta, abstractmethod

class InsteadInterpreterFinder(object, metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def findInsteadInterpreter(self):
        pass

    def checkInterpreterPath(self, path: str):
        return os.path.exists(path)

class InsteadInterpreterFinderMac(InsteadInterpreterFinder):

    paths = [
        '/Applications/Instead.app/Contents/MacOS/sdl-instead'
    ]

    def findInsteadInterpreter(self):
        for path in self.paths:
            if self.checkInterpreterPath(path):
                return path

        return None

if __name__ == "__main__":
    interpreter_finder = InsteadInterpreterFinderMac()
    interpreter_path = interpreter_finder.findInsteadInterpreter()
    print(interpreter_path)
