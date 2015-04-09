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

    def findInsteadInterpreter(self):
        return '/Applications/Instead.app/Contents/MacOS/sdl-instead'
