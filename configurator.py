__author__ = 'jhekasoft'

from abc import ABCMeta, abstractmethod
import json
import os
import shutil


class InsteadManagerConfigurator(object, metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def get_option(self, name: str, default_value=None):
        pass
    #
    # @abstractmethod
    # def set_option(self, name: str, value):
    #     pass
    #
    # @abstractmethod
    # def delete_option(self, name: str):
    #     pass
    #
    # @abstractmethod
    # def create_skeleton_configuration(self):
    #     pass


class InsteadManagerConfiguratorJSON(InsteadManagerConfigurator):
    skeleton_filename = 'instead-manager-settings.json'
    default_config_path = '~/.instead/manager/'
    default_config_filename = 'instead-manager-settings.json'
    config_data = {}

    def __init__(self, base_path):
        self.base_path = base_path

        # Config path
        self.config_path = self.base_path
        if not os.path.isfile(os.path.join(self.config_path, self.default_config_filename)):
            self.config_path = os.path.expanduser(self.default_config_path)
        self.check_and_create_path(self.config_path)
        self.config_filepath = os.path.join(self.config_path, self.default_config_filename)

        if not os.path.isfile(os.path.join(self.config_path, self.default_config_filename)):
            shutil.copyfile(os.path.join(self.base_path, 'skeleton', self.skeleton_filename), self.config_filepath)

        self.config_data = self.read_config_file()

    def check_and_create_path(self, path):
        if not os.path.isdir(path):
            return os.makedirs(path)

        return True

    def read_config_file(self):
        """
        Loading config from JSON-file

        :return:
        """
        json_settings_data = open(self.config_filepath)

        return json.load(json_settings_data)

    def get_option(self, name: str, default_value=None):
        return self.config_data[name] if name in self.config_data else default_value


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.realpath(__file__))
    configurator = InsteadManagerConfiguratorJSON(base_path)
    print(configurator.get_option('repositories1'))
