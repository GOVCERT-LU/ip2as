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


class IP2AS(object):
  def __init__(self, data_path):
    net_as_file = open(data_path, 'rb')
    self.net_as = SubnetTree.SubnetTree()

    for l in net_as_file:
      try:
        ipdescr = IPDescr(l.rstrip())
        net = ipdescr.net
        self.net_as.insert(net, ipdescr)
      except Exception as e:
        # @TODO what to do if no match
        # should not happen but does happen
        pass

    net_as_file.close()

  def get(self, ip):
    try:
      return self.getobj(ip).text
    except:
      return ''

  def getobj(self, ip):
    try:
      return self.net_as[ip]
    except:
      return None


class IPDescr(object):
  def __init__(self, ipas_line):
    # 8966|88.221.217.0/24|ETISALAT-AS Emirates Telecommunications Corporation|EU|ripencc|20060201
    self.asn = ''
    self.net = ''
    self.descr = ''
    self.cc = ''
    self.rir = ''
    self.update = ''

    self.setdata(ipas_line)

  def setdata(self, ipas_line):
    self.asn, self.net, self.descr, self.cc, self.rir, self.update = ipas_line.split('|')
    self.text = ipas_line
    return ipas_line


if __name__ == '__main__':
  ip2as = IP2AS('net_as')

  import sys
  import re

  try:
    for l in sys.stdin:
      if l.endswith('\n'):
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', l):
          print ip2as.get(l[:-1])
        else:
          print 'Invalid IP ->', l[:-1]
  except KeyboardInterrupt:
    sys.stdout.flush()

