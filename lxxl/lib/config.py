
"""Config parser

This class simply provide an accessor on a dict
"""


import os
import yaml
from . import utils


class Config(object):

    __sharedState = {}

    def __init__(self, filename='common.yml'):
        self.__dict__ = self.__sharedState
        if not self.__sharedState:
            self.__files = [filename]
            stream = open(filename, 'r')
            self.__cfg = yaml.load(stream)
            stream.close()

    def include(self, filename):
        self.__files.append(filename)
        stream = open(filename, 'r')
        self.__cfg = utils.deepmerge(self.__cfg, yaml.load(stream))
        stream.close()

    def get(self, key):
        if key in self.__cfg:
            return self.__cfg[key]

    def set(self, key, value):
        self.__cfg[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return (key in self.__cfg)

    def __repr__(self):
        return 'Config: %s' % self.__cfg

    def reload(self):
        files = self.__files
        self.__files = []
        self.__cfg = {}
        for filename in files:
            self.include(filename)


class ConfigError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
