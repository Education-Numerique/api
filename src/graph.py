#!/usr/bin/env python
import os
import sys

# insert contrib libs just after current directory
ROOT = os.path.dirname(__file__)

from lib.config import Config
from lib import log, app, storage

CONFIG_FILE = os.path.join(ROOT, 'conf', 'common.yml')
STORAGE_FILE = os.path.join(ROOT, 'conf', 'storage.yml')
ROUTING_FILE = os.path.join(ROOT, 'conf', 'routing', 'graph')
COMMON_ROUTING_FILE = os.path.join(ROOT, 'conf', 'routing', 'common.yml')


cfg = Config(CONFIG_FILE)
cfg.include(STORAGE_FILE)
cfg.include(os.path.join(ROUTING_FILE, 'users.yml'))
cfg.include(os.path.join(ROUTING_FILE, 'usergroups.yml'))
cfg.include(os.path.join(ROUTING_FILE, 'revisions.yml'))
cfg.include(os.path.join(ROUTING_FILE, 'categories.yml'))
cfg.include(os.path.join(ROUTING_FILE, 'activities.yml'))

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
    make_server('localhost', 8082, application).serve_forever()
