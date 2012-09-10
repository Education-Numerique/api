# This file is part of ZWS (Zoomorama Web Services)
#
# ZWS has been written by Samuel Alba <sam.alba@gmail.com>
# - for Zoomorama.
#
# Development started on November 2008.
#
# Zoomorama WebServices
# Copyright (C) 2008, 2009, 2010 Zoomorama, written by Samuel Alba
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


"""Config parser

This class simply provide an accessor on a dict
"""


import os
import yaml
from lib import utils


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
