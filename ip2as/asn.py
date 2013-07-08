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
