"""log module: a python logging wrapper"""

import os
import logging

from .config import Config


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
