#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'Georges Toth'
__email__ = 'georges.toth@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Georges Toth'
__license__ = 'GPL v3+'

#
# mail feature extractor
# submits results to a remote mailm0n server via REST API
#

import sys
import os
try:
  import ConfigParser as configparser
except ImportError:
  import configparser
from optparse import OptionParser
import json
import ip2as.api


def main(api_url, api_key, proxies):
  api = gclu_pdns.api.PDNSApi(api_url, api_key, verify_ssl=False, proxies=proxies)

  j = api.get_asn('16876')

  j = ip2as.api.json_pretty_print(j)
  print(j)


if __name__ == '__main__':
  config_file = os.path.expanduser('~/.ip2as_cli.conf')
  if not os.path.isfile(config_file):
    print('Fatal error: config file not found!')
    sys.exit(1)

  config = configparser.ConfigParser()
  config.read(config_file)

  try:
    api_url = config.get('api', 'url')
    api_key = config.get('api', 'key')
    http_proxy = config.get('api', 'http_proxy')
    https_proxy = config.get('api', 'https_proxy')
  except:
    print('Fatal error: invalid config file!')
    sys.exit(1)

  proxies = {}
  if not http_proxy == '':
    proxies['http'] = http_proxy
  if not https_proxy == '':
    proxies['https'] = https_proxy

  api = ip2as.api.IP2ASApi(api_url, api_key, verify_ssl=False, proxies=proxies)

  parser = OptionParser()
  parser.add_option('-a', dest='asn', type='string', default='',
                    help='AS number')
  parser.add_option('-i', dest='ip', type='string', default='',
                    help='IP')

  (options, args) = parser.parse_args()

  if options.asn == '' and options.ip == '':
    parser.print_help()
    exit(1)

  if not options.asn == '':
    j = api.get_asn(options.asn)
  elif not options.ip == '':
    j = api.get_ip(options.ip)
  else:
    print('Fatal error: nothing to do O_o, check parameters!')
    print()
    parser.print_help()
    exit(1)

  j = ip2as.api.json_pretty_print(j)
  print(j)
