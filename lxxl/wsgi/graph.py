#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
ROOT = os.path.join(os.path.dirname(__file__), '../')

from lxxl.lib.config import Config
from lxxl.lib import log, app, storage

CONFIG_FILE = os.path.join(ROOT, 'conf', 'common.yml')
STORAGE_FILE = os.path.join(ROOT, 'conf', 'storage.yml')
ROUTING_FILE = os.path.join(ROOT, 'conf', 'routing', 'graph')
COMMON_ROUTING_FILE = os.path.join(ROOT, 'conf', 'routing', 'common.yml')


cfg = Config(CONFIG_FILE)
cfg.include(STORAGE_FILE)
cfg.include(os.path.join(ROUTING_FILE, 'users.yml'))
cfg.include(os.path.join(ROUTING_FILE, 'usergroups.yml'))
cfg.include(os.path.join(ROUTING_FILE, 'activities.yml'))
cfg.include(os.path.join(ROUTING_FILE, 'blob.yml'))


cfg.include(COMMON_ROUTING_FILE)

routing = cfg.get('common_routing')
routing = routing + cfg.get('routing')

#log.init()

application = app.Controller()
application.ROOT = ROOT
application.addRoutingFromConfig('*', routing)


log.info('Roxee Data server is running (#%s).' % os.getpid())


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    make_server('localhost', 8083, application).serve_forever()
