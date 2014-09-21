#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# insert contrib libs just after current directory
ROOT = os.path.join(os.path.dirname(__file__), '../')


from lxxl.lib.config import Config
from lxxl.lib import log, app, storage


CONFIG_FILE = os.path.join(ROOT, 'conf', 'common.yml')
STORAGE_FILE = os.path.join(ROOT, 'conf', 'storage.yml')
ROUTING_FILE = os.path.join(ROOT, 'conf', 'routing', 'authentication')
COMMON_ROUTING_FILE = os.path.join(ROOT, 'conf', 'routing', 'common.yml')


cfg = Config(CONFIG_FILE)
cfg.include(STORAGE_FILE)
cfg.include(os.path.join(ROUTING_FILE, 'admin.yml'))
cfg.include(COMMON_ROUTING_FILE)

routing = cfg.get('common_routing')
routing = routing + cfg.get('routing')

#log.init()

application = app.Controller()
application.addRoutingFromConfig('*', routing)


log.info('LxxL Data Server is running (#%s).' % os.getpid())


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    make_server('localhost', 8081, application).serve_forever()
