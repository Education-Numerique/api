#!/usr/bin/env puke
# -*- coding: utf8 -*-


@task("default")
def default():
    pass

@task("uwsgi")
def uwsgi():
    System.check_package('python3', '>=3.2')
    System.check_package('python3-dev', '>=3.2', platform = System.LINUX)
    System.check_package('uwsgi-plugin-python3', platform = System.LINUX)
    System.check_package('uwsgi')
    System.check_package('libyaml-dev', platform = System.LINUX)

    e = VirtualEnv()
    e.create('/opt/puke/lxxl', 'python3')
    e.sh('python3 setup.py install', output=False, header="Install lxxl")