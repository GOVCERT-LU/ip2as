#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Georges Toth'
__email__ = 'georges.toth@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Georges Toth'
__license__ = 'GPL v3+'

#
# IP2AS client API
#

import json
import urllib
import urllib2



class IP2ASApi(object):
  def __init__(self, api_url, api_key, http_timeout=5, verify_ssl=False, proxies={}):
    self.api_url = api_url
    self.api_key = api_key
    self.verify_ssl = verify_ssl
    self.proxies = proxies

    proxy = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)

  def __request(self, method, data=None, query_args=None, extra_headers=None):
    url = '{0}/{1}'.format(self.api_url, method)

    if not query_args is None and len(query_args) > 0:
      url = '{0}/?{1}'.format(url, urllib.urlencode(query_args))

    query_data = None
    if not data is None:
      query_data = json.dumps(data)

    headers = {'Content-Type': 'application/json; charset=utf-8', 'key' : self.api_key}

    if extra_headers:
      for k, v in extra_headers.items():
        headers[k] = v

    r = urllib2.Request(url, data=query_data, headers=headers)
    try:
      res = urllib2.urlopen(r).read()
    except urllib2.HTTPError, e:
      raise Exception('Error ({0})'.format(e.code))
    except urllib2.URLError, e:
      raise Exception('Error ({0})'.format(e.reason.args[1]))

    # @FIXME why do we need to load json twice? -> doing it once returns an unquoted string O_o
    res = json.loads(res)

    return json.loads(res)

  def get_asn(self, asn):
    return self.__request('get_asn', query_args={'asn' : asn})

  def get_ip(self, ip):
    return self.__request('get_ip', query_args={'ip' : ip})

  def get_ip_str(self, ip):
    nets = self.get_ip(ip)
    net = None
    asns = ''

    for net in nets:
      if not asns == '':
        asns += ' '
      asns += net['asn']

    return '{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}'.format('|', asns, net['net'], net['name'], net['cc'], net['rir'], net['timestamp'])


def json_pretty_print(j):
  return json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))
