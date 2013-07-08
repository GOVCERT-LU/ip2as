#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of ip2as.
#
# ip2as is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ip2as is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rt_bot.  If not, see <http://www.gnu.org/licenses/>.


import SubnetTree
import json


class ASN(object):
  def __init__(self, asn):
    self.asn = asn
    self.name = ''
    self.cc = ''
    self.rir = ''
    self.timestamp = ''
    self.nets = {}

  def __str__(self):
    ret = 'ASN: {0} | name: {1} | CC: {2} | RIR: {3} | timestamp: {4}'.format(self.asn, self.name, self.cc, self.rir, self.timestamp)

    for n, v in self.nets.items():
      ret += '\n\tNet: {0}, {1}'.format(n, v)

    return ret

  def todict(self):
    ret = {'asn': self.asn, 'name': self.name, 'cc': self.cc, 'rir': self.rir,
           'timestamp': self.timestamp, 'nets': {}}

    for n, v in self.nets.items():
      ret['nets'][n] = {'cc': v['cc'], 'rir': v['rir'], 'timestamp': v['timestamp']}

    return ret

  def tojson(self):
    return json.dumps(self.todict())

  def fromdict(self, j):
    '''
    "name": "EYEMG - EYEMG - interactive media group", "cc": "US", "timestamp": "20070524", "rir": "arin", "asn": "11542"
    "nets": {"208.79.156.0/22": {"cc": "US", "timestamp": "20070621", "rir": "arin"}
    '''
    self.name = j['name']
    self.cc = j['cc']
    self.rir = j['rir']
    self.timestamp = j['timestamp']

    for net, v in j['nets'].items():
      self.nets[net] = v

  def getnet(self, net):
    return {'asn': self.asn, 'net': net, 'name': self.name, 'cc': self.nets[net]['cc'], 'rir': self.nets[net]['rir'], 'timestamp': self.nets[net]['timestamp']}


class IP2AS(object):
  def __init__(self, data_path):
    self.net_as = SubnetTree.SubnetTree()
    self.d_asn = {}
    self.net_as_map = {}

    net_as_file = open(data_path, 'rb')
    net_as_json = json.load(net_as_file)
    net_as_file.close()

    for asn, v in net_as_json.items():
      '''
       "11542": {
          "name": "EYEMG - EYEMG - interactive media group", "cc": "US", "timestamp": "20070524", "rir": "arin",
          "nets": {"208.79.156.0/22": {"cc": "US", "timestamp": "20070621", "rir": "arin"}
                  },
          "asn": "11542"}
      '''
      self.d_asn[asn] = ASN(asn)
      self.d_asn[asn].fromdict(v)

      for net in self.d_asn[asn].nets.keys():
        '''A single net may be announced in various ASNs'''
        self.net_as.insert(str(net), net)

        if not net in self.net_as_map:
          self.net_as_map[net] = []

        if not asn in self.net_as_map[net]:
          self.net_as_map[net].append(asn)

  def getasn(self, asn):
    if asn in self.d_asn:
      return self.d_asn[asn].todict()

    raise KeyError('No such ASN')

  def getasn_str(self, asn):
    asn_ = self.getasn(asn)

    return '{1}{0}{2}{0}{3}{0}{4}{0}{5}'.format('|', asn_['asn'], asn_['cc'], asn_['rir'], asn_['timestamp'], asn_['name'])

  def getip(self, ip):
    try:
      net = self.net_as[str(ip)]

      ret = []
      for asn in self.net_as_map[net]:
        ret.append(self.d_asn[asn].getnet(net))

      return ret
    except KeyError:
      raise Exception('{0} not found'.format(ip))

  def getip_str(self, ip):
    nets = self.getip(ip)
    net = None
    asns = ''

    for net in nets:
      if not asns == '':
        asns += ' '
      asns += net['asn']

    return '{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}'.format('|', asns, net['net'], net['name'], net['cc'], net['rir'], net['timestamp'])

  def get(self, ip):
    return self.getip_str(ip)




if __name__ == '__main__':
  import ConfigParser

  # Get ctienet path
  config = ConfigParser.RawConfigParser()
  config.read('/opt/govcert/etc/govcert_paths.ini')
  ini_path = config.get('main', 'ini')
  config.read(ini_path + '/' + 'ip2as.ini')
  ip2as_dat = config.get('main', 'ip2as_bin_dat')
  ####################

  ip2as = IP2AS(ip2as_dat)

  ip = '192.0.43.10'
  print ip2as.getip_str(ip)

  asn = '16876'
  print ip2as.getasn_str(asn)
