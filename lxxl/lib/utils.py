import collections
import time
import random
import errno
import os
import tempfile

def randomBase62(length=16):
    import random

    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choice(ALPHABET) for i in range(length))


def quacks_like_dict(object):
    """Check if object is dict-like"""
    return isinstance(object, collections.Mapping)


def deepmerge(a, b):
    """Merge two deep dicts non-destructively

    Uses a stack to avoid maximum recursion depth exceptions

    >>> a = {'a': 1, 'b': {1: 1, 2: 2}, 'd': 6}
    >>> b = {'c': 3, 'b': {2: 7}, 'd': {'z': [1, 2, 3]}}
    >>> c = merge(a, b)
    >>> from pprint import pprint; pprint(c)
    {'a': 1, 'b': {1: 1, 2: 7}, 'c': 3, 'd': {'z': [1, 2, 3]}}
    """
    assert quacks_like_dict(a), quacks_like_dict(b)
    dst = a.copy()

    stack = [(dst, b)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                current_dst[key] = current_src[key]
            else:
                if quacks_like_dict(current_src[key]) and quacks_like_dict(current_dst[key]):
                    stack.append((current_dst[key], current_src[key]))
                elif isinstance(current_src[key], list) and isinstance(current_dst[key], list):
                    current_dst[key] = (current_dst[key] + current_src[key])
                else:
                    current_dst[key] = current_src[key]
    return dst


# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.




class Pidfile(object):
    """\
    Manage a PID file. If a specific name is provided
    it and '"%s.oldpid" % name' will be used. Otherwise
    we create a temp file using os.mkstemp.
    """

    def __init__(self, fname):
        self.fname = fname
        self._fsname = os.path.join(tempfile.gettempdir(), fname)
        self.pid = None

    def create(self, pid):
        oldpid = self.validate()
        if oldpid:
            if oldpid == os.getpid():
                return
            raise RuntimeError("Already running on PID %s " \
                "(or pid file '%s' is stale)" % (os.getpid(), self.fname))

        self.pid = pid

        # Write pidfile
        fd, fname = tempfile.mkstemp()
        os.write(fd, ("%s\n" % self.pid).encode('utf-8'))
        os.rename(fname, self._fsname)
        os.close(fd)

        # set permissions to -rw-r--r--
        os.chmod(self._fsname, 420)

    def unlink(self):
        """ delete pidfile"""
        try:
            with open(self._fsname, "r") as f:
                pid1 =  int(f.read() or 0)

            if pid1 == self.pid:
                os.unlink(self._fsname)
        except:
            pass

    def validate(self):
        """ Validate pidfile and make it stale if needed"""
        if not self._fsname:
            return
        try:
            with open(self._fsname, "r") as f:
                wpid = int(f.read() or 0)

                if wpid <= 0:
                    return

                try:
                    os.kill(wpid, 0)
                    return wpid
                except OSError as e:
                    if e.errno == errno.ESRCH:
                        return
                    raise
        except IOError as e:
            if e.errno == errno.ENOENT:
                return
            raise