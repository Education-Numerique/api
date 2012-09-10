# Copyright (c) 2011 Samuel Alba, sam.alba@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import sys
from webob import exc

PY3 = sys.version_info[0] == 3


def unpack(iterable):
    """ Iter through an iterable container by unpacking by pair """
    it = iter(iterable)
    while True:
        try:
            if PY3:
                yield it.__next__(), it.__next__(), it.__next__(), it.__next__()
            else:
                yield it.next(), it.next(), it.next(), it.next()
        except StopIteration:
            break


class Root(object):

    def __call__(self, environ, start_response, params={}):
        if hasattr(self, params['action']):
            call = getattr(self, params['action'])
            if callable(call):
                try:
                    resp = call(environ, params)
                except exc.HTTPException as resp:
                    pass

                return resp(environ, start_response)

        resp = exc.HTTPNotImplemented()
        return resp(environ, start_response)


class Router(object):
    reParams = re.compile(':([a-z]+)')

    def __init__(self):
        self._routes = {'default': []}
        self._compile = lambda value: [(re.compile(i), j, k, l)
                                       for i, j, k, l in unpack(value)]

    def __setitem__(self, key, value):
        if key == '*':
            key = 'default'
        self._routes[key] = self._compile(value)

    def __getitem__(self, key):
        return self._routes[key]

    def append(self, value, vhost='default'):
        self._routes[vhost].append(self._compile(value))

    def matchRoutes(self, namespace, replace, host='default'):
        infos = namespace.split('.')
        #pad array
        infos = infos + ['*'] * (3 - len(infos))

        service = infos[0] if infos[0] != '*' else True
        module = infos[1] if infos[1] != '*' else True
        action = infos[2] if infos[2] != '*' else True

        urls = []

        for route in self._routes[host]:
            (m, obj, vars, params) = route
            if (service == True or params['service'] in service) and \
                (module == True or params['module'] in module) and \
                    (action == True or params['action'] in action):
                url = params['pattern']

                for name in vars:
                    if name not in replace:
                        continue

                    url = url.replace(':' + name, replace[name]).rstrip('\/?')

                urls.append(url.strip('^').strip('$'))

        return urls

    def getRoute(self, namespace, replace, host='default'):
        infos = namespace.split('.')

        for route in self._routes[host]:
            (m, obj, vars, params) = route

            if params['service'] == infos[0] and \
                params['module'] == infos[1] and \
                    params['action'] == infos[2]:
                url = params['pattern']

                for name in vars:
                    if name not in replace:
                        continue

                    url = url.replace(':' + name, replace[name]).rstrip('\/?')

                return url.strip('^').strip('$')

    def _get_routes(self, environ):
        host_header = environ.get('HTTP_HOST', 'default').split(':')[0]
        if not host_header in self._routes:
            return self._routes['default']

        return self._routes[host_header]

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '/')
        meth = environ.get('REQUEST_METHOD', 'GET').lower()

        for route in self._get_routes(environ):
            (m, obj, vars, params) = route

            if params['method'] != '*' and meth not in params['method']:
                continue

            exp = m.match(path_info)
            if exp:
                #return values
                index = 1
                paramsIndex = Router.reParams.findall(params['pattern'])
                for key in paramsIndex:
                    try:
                        params[key] = exp.group(index)
                    except:
                        pass
                    index = index + 1

                return obj(environ, start_response, params)
        resp = exc.HTTPNotFound()
        return resp(environ, start_response)
