__author__ = 'jhekasoft'

from abc import ABCMeta, abstractmethod


class InsteadManagerConfigurator(object, metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def get_option(self, name: str):
        pass

    @abstractmethod
    def set_option(self, name: str, value):
        pass

    @abstractmethod
    def delete_option(self, name: str):
        pass

    @abstractmethod
    def create_skeleton_configuration(self):
        pass


# class InsteadManagerConfiguratorJSON(InsteadManagerConfigurator):
