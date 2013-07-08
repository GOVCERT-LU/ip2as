#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Georges Toth'
__email__ = 'georges.toth@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Georges Toth'
__license__ = 'GPL v3+'

#
# REST server API for IP2AS data
#

import cherrypy
import os
import syslog
import sys
try:
  import ConfigParser as configparser
except ImportError:
  import configparser
import json
from ip2as.ip2as import IP2AS


def is_authorized():
  if not cherrypy.request.headers.get('key', '') in cherrypy.config['api_keys']:
    raise cherrypy.HTTPError(403, 'Forbidden')


def audit():
  params = {}

  if cherrypy.request.json:
    for k in cherrypy.request.json:
      params[k] = cherrypy.request.json[k]

  log('{0} {1} {2} {3}'.format(cherrypy.request.headers.get('remote-addr', 'NONE'), cherrypy.request.headers.get('key', ''),
      cherrypy.request.request_line, str(params)))


cherrypy.tools.is_authorized = cherrypy.Tool('before_handler', is_authorized, priority=49)
cherrypy.tools.audit = cherrypy.Tool('before_handler', audit, priority=50)


def log(msg, priority=syslog.LOG_INFO):
  '''
  Central logging method

  :param msg: message
  :param priority: message priority
  :type msg: str
  :type priority: syslog.LOG_*
  '''

  syslog.syslog(priority, msg)


class Manage(object):
  def __init__(self, ip2as):
    self.ip2as = ip2as

  @cherrypy.expose
  @cherrypy.tools.audit()
  @cherrypy.tools.is_authorized()
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  def get_asn(self):
    params = cherrypy.request.json

    try:
      asn = self.ip2as.getasn(params['asn'])
    except KeyError:
      raise cherrypy.HTTPError(404, 'Nothing found')

    cherrypy.response.status = 200
    return json.dumps(asn)

  @cherrypy.expose
  @cherrypy.tools.audit()
  @cherrypy.tools.is_authorized()
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  def get_ip(self):
    params = cherrypy.request.json

    try:
      ip = self.ip2as.getip(params['ip'])
    except KeyError:
      raise cherrypy.HTTPError(404, 'Nothing found')

    cherrypy.response.status = 200
    return json.dumps(ip)



def error_page_403(status, message, traceback, version):
  return 'Error {0} - {1}'.format(status, message)

cherrypy.config.update({'error_page.403': error_page_403})


def application(environ, start_response):
  syslog.openlog('ip2as_wsgi_server', logoption=syslog.LOG_PID)
  myprefix = os.path.dirname(os.path.abspath(__file__))
  wsgi_config = myprefix + '/wsgi_api.ini'

  if not os.path.exists(wsgi_config):
    wsgi_config = '/etc/ip2as_wsgi_api.ini'
  if not os.path.exists(wsgi_config):
    log('Fatal error: config file not found!', priority=syslog.LOG_ERR)
    sys.exit(1)

  config = configparser.ConfigParser()
  config.read(wsgi_config)
  ip2as_dat = config.get('ip2as', 'ip2as_bin_dat').strip('\'')

  ip2as = IP2AS(ip2as_dat)

  cherrypy.config['tools.encode.on'] = True
  cherrypy.config['tools.encode.encoding'] = 'utf-8'
  cherrypy.config.update(config=wsgi_config)

  cherrypy.tree.mount(Manage(ip2as), '/', config=wsgi_config)

  return cherrypy.tree(environ, start_response)


if __name__ == '__main__':
  syslog.openlog('ip2as_wsgi_server', logoption=syslog.LOG_PID)
  myprefix = os.path.dirname(os.path.abspath(__file__))
  wsgi_config = myprefix + '/wsgi_api.ini'

  if not os.path.exists(wsgi_config):
    wsgi_config = '/etc/ip2as_wsgi_api.ini'
  if not os.path.exists(wsgi_config):
    log('Fatal error: config file not found!', priority=syslog.LOG_ERR)
    sys.exit(1)

  config = configparser.ConfigParser()
  config.read(wsgi_config)
  ip2as_dat = config.get('ip2as', 'ip2as_bin_dat').strip('\'')

  ip2as = IP2AS(ip2as_dat)

  cherrypy.config['tools.encode.on'] = True
  cherrypy.config['tools.encode.encoding'] = 'utf-8'
  cherrypy.config.update(config=wsgi_config)

  log('starting')
  cherrypy.quickstart(Manage(ip2as), '/', config=wsgi_config)
