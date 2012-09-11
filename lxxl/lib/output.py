from . import app
import time
import json
import re
import datetime
import hashlib
from .utils import deepmerge


def error(msg, code=400, internal=100):
    resp = app.Controller().getResponse()
    resp.status = code
    if isinstance(msg, dict):
        msg = json.JSONEncoder().encode(msg)
    else:
        msg = '"%s"' % msg
    resp.text = '{  "time" : "' + str(int(time.time())) + '", \
                "error" : ' + msg + ', \
                "code" : "' + str(internal) + '"}\n'

    if code == 500:
        print("### Error %s" % msg)

    raise app.Error('HTTP Error')


def authenticated():
    resp = app.Controller().getResponse()
    resp.status = 202
    resp.text = '{  "time" : "' + str(int(time.time())) + '", \
                "message" : "authenticated"}\n'


def success(msg, code):
    resp = app.Controller().getResponse()
    resp.status = code

    if not isinstance(msg, str):

        #bad bad bad perf
        dthandler = lambda obj: "%sZ" % obj.isoformat(
        ) if isinstance(obj, datetime.datetime) else None
        resp.text = json.dumps(msg, default=dthandler)

        #resp.text = json.JSONEncoder().encode(msg)

        return True

    resp.text = '{ "time" : "' + str(int(time.time())) + '", \
                "message" : "' + msg + '"}\n'


def varnishCacheManager(ttl=None, vary=''):
    resp = app.Controller().getResponse()

    if ttl:
        if ttl.lower() == '1 year':
            ttl = '1Y'
        elif ttl.lower() == '1 minute':
            ttl = '1m'

        resp.headers['Rox-Ttl'] = ttl

    if type(vary) is not str:
        vary = ', '.join(vary)

    if vary:
        resp.headers['Vary'] = vary


def cacheManager(max=3600 * 24 * 2, age=0, handleEtags=False):
    resp = app.Controller().getResponse()
    req = app.Controller().getRequest()

    expire = int(time.time() - age + max)

    resp.headers['Cache-Control'] = 'private, max-age=%s' % max
    resp.headers['Age'] = '%s' % age
    resp.headers['Expires'] = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expire))

    if handleEtags == True:
        resp.etag = hashlib.sha1(resp.text.encode('utf-8')).hexdigest()

    if 'if-none-match' not in req.headers:
        return True

    #Handle 304
    noneMatch = req.headers['if-none-match'].strip('"')
    if noneMatch == resp.etag:
        resp.status = 304
        resp.text = ''


def noCache():
    resp = app.Controller().getResponse()

    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = 'Thu, 19 Nov 1981 08:52:00 GMT'
    future = int(time.time() + 3600 * 24 * 365 * 2)
    resp.headers['Last-Modified'] = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(future))


def __getAge():
    days = int(time.time() / (3600 * 24)) % 7
    #shift monday to 0
    if days >= 4 and days <= 6:
        days -= 4
    else:
        days += 3

    midnight = datetime.datetime.utcnow(
    ).replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.datetime.utcnow()
    delta = now - midnight

    #localtime
    lastRefresh = datetime.datetime.now(
    ) - datetime.timedelta(days=days, seconds=int(delta.seconds))
    #get utc timestamp
    lastRefresh = time.mktime(lastRefresh.timetuple())

    age = (int(time.time() - lastRefresh))
    max = (3600 * 24 * 7)
    expire = int(time.time() - age + max)

    return {'age': age, 'max': max, 'expire': expire}


def __makeobject(keys, value):

    r = lambda x = value: x
    for i in reversed(keys):
        f = lambda x = i: x
        r = lambda x = r, y = f: {y(): x()}

    return r()


def unpack(iterable):
    """ Iter through an iterable container by unpacking by pair """
    it = iter(iterable)
    while True:
        try:
            yield it.__next__(), it.__next__()
        except StopIteration:
            break
