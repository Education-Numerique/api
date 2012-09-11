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


"""log module: a python logging wrapper"""

import os
import logging

from lib.config import Config


def init():
    cfg = Config()
    dir = cfg.get('log_directory')

    if not os.path.exists(dir):
        print('Creating %s' % dir)
        os.makedirs(dir)
    level = logging.INFO
    if cfg.get('node_context') == 'dev':
        level = logging.DEBUG
    logging.basicConfig(level=level,
                        format='%(asctime)s #' + str(
                        os.getpid()) + ' %(levelname)s: %(message)s',
                        filename=os.path.join(dir, 'roxee-data.log'),
                        filemode='a')


def debug(msg):
    logging.debug(msg)


def info(msg):
    logging.info(msg)


def warning(msg):
    logging.warning(msg)
