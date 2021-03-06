clients.lxxl.api
=========================

Travis: http://travis-ci.org/Education-Numerique/api

Api services for lxxl.

Linux (Ubuntu 12.10 ) installation
=========================
In the following steps, we setup a MongoDB and a Nginx server and install a Python 3 virtualenv to run the service.

**1. As root** adapt these to your favorite Linux flavor

Add 10-gen repository to sources.list:
```deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen```

Add key:
```apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10```

Get system dependencies:
```aptitude install python3-pip python-pip git nginx uwsgi mongodb20-10gen memcached uwsgi-plugin-python3 python-dev python3.3-dev libyaml-dev```


**2. Also as root** let us be cross-distro (virtualenv)

Get venv:
```pip install virtualenv```

Prepare directory:
```mkdir -p /home/lxxl-deploy; cd /home/lxxl-deploy; chown www-data /home/lxxl-deploy```

Prepare uwsgi:
a) inherited config
```
cd /etc/uwsgi
vi inherited_config.ini
```
```
[uwsgi]
autoload = true
# XXX macosx testing
# plugins = python32
# XXX test macosx
# no-site = true

daemonize = /var/log/uwsgi/app/%(lxxl).log

max-request = 10000

# enable master process manager
master = true

# spawn 2 uWSGI worker processes
workers = 1

# automatically kill workers on master's death
no-orphans = true

# write master's pid in file /run/uwsgi/<confname>/pid
pidfile = /var/run/uwsgi/app/%(lxxl)/pid

# bind to UNIX socket at /run/uwsgi/<confname>/socket
socket = /var/run/uwsgi/app/%(lxxl)/socket

# set mode of created UNIX socket
chmod-socket = 660

# place timestamps into log
log-date = true

# user identifier of uWSGI processes
uid = www-data

# group identifier of uWSGI processes
gid = www-data

enable-threads = true
reload-mercy = 8
memory-report = false
harakiri = 30
harakiri-verbose = true
post-buffering = 8192
```

```
vi /etc/default/uwsgi
```
```
INHERITED_CONFIG=/etc/uwsgi/inherited_config.ini
```

b) prepare workers
```
cd /etc/uwsgi/apps-available
vi lxxl.wildbull.ini
```
```
[uwsgi]
  workers = 1
  listen = 100
  home = /home/lxxl-deploy/virtualenv 
  module = lxxl.wsgi.wildbull
  plugins = python32
  lxxl = lxxl.wildbull
```

```
vi lxxl.graph.ini
```
```
[uwsgi]
  workers = 1
  listen = 100
  home = /home/lxxl-deploy/virtualenv
  module = lxxl.wsgi.graph
  plugins = python32
  lxxl = lxxl.graph 
```

```
vi lxxl.auth.front.ini
```
```
[uwsgi]
  workers = 1
  listen = 100
  home = /home/lxxl-deploy/virtualenv
  module = lxxl.wsgi.authentication-front
  plugins = python32
  lxxl = lxxl.auth.front
```

```
vi lxxl.auth.admin.ini
```
```
[uwsgi]
  workers = 1
  listen = 100
  home = /home/lxxl-deploy/virtualenv
  module = lxxl.wsgi.authentication-admin
  plugins = python32
  lxxl = lxxl.auth.admin
```

Enable apps:
```cd ../apps-enabled; ln -s ../apps-available/*.ini .;```


**3. Get and install puke:**
```pip install puke```
Check installation details at : https://github.com/webitup/puke

**4. Get the API virtualenv up and running**
Be sure to understand what you do at this step !!! - RTFM

Downgrade to www-data:
```
cd /home/lxxl-deploy/ 
su www-data
```

Fetch sources: ```git clone https://github.com/Education-Numerique/api.git```

Setup venv:
```virtualenv -p python3.2 --no-site-packages /home/lxxl-deploy/virtualenv```

Now setup: ```cd api; source ../virtualenv/bin/activate; python3 setup.py install```

**5. Back to root, restart uwsgi:**
```
/etc/init.d/uwsgi restart
```

Doesn't work? Check /var/log/uwsgi and investigate.


**6. Configure server (Nginx)**
Your Nginx conf will probably grow a bit more complex than in the following example. This is just for basic points to consider ...
In the following config example, I defined the API server on port 80. 
Good practice would require similar config for SSL on port 443.

```
vi /etc/nginx/sites-available/lxxl.api
```

Proxy/load balancing defs for the Python workers : similar config needed for auth-front on 8082, graph on 8083 and auth-admin on 8084 ...  

```
upstream lxxl_wildbull_backend {
        server unix:///var/run/uwsgi/app/lxxl.wildbull/socket;
}
...
```

```
server {
  listen 80;
  server_name ~^api.education-et-numerique.fr$;
  fastcgi_buffers 256 8k;
  location /  {
    include uwsgi_params;

  add_header X-Content-Type-Options 'nosniff';
# add_header X-Frame-Options 'Allow';
  add_header X-UA-Compatible 'IE=Edge,chrome=1';
  add_header X-XSS-Protection '0';
  charset utf-8;
  gzip on;
  gzip_types application/json application/x-javascript text/css;
  charset_types application/javascript;
  
    access_log /var/log/nginx/access.lxxl.wildbull.log;
    error_log /var/log/nginx/error.lxxl.wildbull.log;

    uwsgi_pass lxxl_wildbull_backend;
  }
}
```

Don't forget the symbolic link on sites-enabled and nginx reload ... 

**7. Front**

*Either do it the hard way* (not for the faint of heart), use the forks and build them:
```
# RVM is supposedly the sane way to use Rubeshit
curl -L https://get.rvm.io | bash -s stable --ruby
/var/www/.rvm/scripts/rvm
source ~/.bashrc
gem install bundler
# Ruby being what it is, you may need to manually fuckerize your path to have bundle behave

# Other build dependencies
sudo aptitude install npm node p7zip-full subversion openjdk-7-jre libxml2-dev

# Build everything
git clone https://github.com/Education-Numerique/airstrip.js.git
git clone https://github.com/Education-Numerique/spitfire.js.git
git clone https://github.com/Education-Numerique/jsboot.js.git
git clone https://github.com/Education-Numerique/authoring.js.git
cd airstrip.js; puke; cd -;
cd spitfire.js; puke; cd -;
cd jsboot.js; puke; cd -;
cd authoring.js; puke; cd -;
```

*Or do yourself a favor* 
Get support from Education-et-numerique and just use a release tarball, to be extracted into /home/lxxl-deploy/lxxl, or even to take care of the complete intallation process.

**And, ha, don't forget to init the mongo database ;).**


Random OSX notes
=========================

WARNING: these notes are largely unverified! you are supposed to know how to swim if you are here!

If using OSX, you need a working developer environment. That is: OSX >= 10.6, with XCode >= 4.2 (or command line tools if you are using Lion or Mountain Lion).

Then install brew:
```mkdir -p lxxl-authoring/dependencies
cd lxxl-authoring/dependencies
mkdir homebrew && curl -L https://github.com/mxcl/homebrew/tarball/master | tar xz --strip 1 -C homebrew```

Export homebrew path in your .profile

```export PATH=$HOME/lxxl-authoring/dependencies/homebrew/bin:$HOME/lxxl-authoring/dependencies/homebrew/sbin:$PATH```

Init brew

```brew update; brew upgrade```


Get git if you don't have it

```brew install git```

Get python3:

```brew install python3```

Doesn't work? You likely have an old setup. Try with --use-clang.

Get python2

```brew install python```

Amend your path

```export PATH=$HOME/lxxl-authoring/dependencies/homebrew/share/python3:$HOME/lxxl-authoring/dependencies/homebrew/share/python:$HOME/lxxl-authoring/dependencies/homebrew/bin:$HOME/lxxl-authoring/dependencies/homebrew/sbin:$PATH```

Double-check everything is ok 

```which python```
```which easy_install```

Now you need pip, puke, and the base server dependencies

```easy_install pip```

```pip install --upgrade puke```

```brew install --universal pcre``` (likely specific to old OSXes)

```brew install uwsgi```

Amend the pukefile so it reads:

e.create('~/lxxl-authoring/virtualenv', 'python3')


Now puke

```puke uwsgi```
