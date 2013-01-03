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
import mmap

try:
  import msgpack
  import_msgpack = True
except:
  import_msgpack = False



class IP2AS(object):
  def __init__(self, data_path, use_msgpack=False):
    if use_msgpack and not import_msgpack:
      raise Exception('Fatal error: specified to use msgpack, but msgpack module not installed')

    self.net_as_file = open(data_path, 'rb')
    self.net_as = SubnetTree.SubnetTree()

    if use_msgpack:
      self.init_from_msgpack()
    else:
      self.init_from_csv()

    self.net_as_file.close()

  def init_from_csv(self):
    net_as_mmap = mmap.mmap(self.net_as_file.fileno(), 0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)

    for l in iter(net_as_mmap.readline, ''):
      try:
        ipdescr = self.parse_line(l[:-1])
        self.net_as.insert(ipdescr['n'], ipdescr)
      except ValueError:
        print 'Value error: this mostly indicates that you are trying to use\
 a binary data file but did not specify to use msgpack\n'
        raise
      except Exception as e:
        # @TODO what to do if no match
        # should not happen but does happen
        print e
        pass

    net_as_mmap.close()

  def init_from_msgpack(self):
    ip2as_list = msgpack.unpack(self.net_as_file, use_list=False)

    for k in ip2as_list:
      try:
        self.net_as.insert(k['n'], k)
      except Exception as e:
        # @TODO what to do if no match
        # should not happen but does happen
        print e
        pass

  def get(self, ip):
    try:
      ipdescr = self.net_as[ip]

      return '{0}|{1}|{2}|{3}|{4}|{5}'.format(ipdescr['a'], ipdescr['n'],
        ipdescr['d'], ipdescr['c'], ipdescr['r'], ipdescr['u'])
    except KeyError:
      return '{0} not found'.format(ip)

  def parse_line(self, ip2as_line):
    asn, net, descr, cc, rir, update = ip2as_line.split('|')

    if update == '':
      update = 0
    else:
      update = int(update)

    # a: asn, n: net, d: descr, c: cc, r: rir, u: update
    return {'a' : asn, 'n' : net, 'd' : descr, 'c' : cc,
            'r' : rir, 'u' : update}



if __name__ == '__main__':
  ip2as = IP2AS('net_as.bin', use_msgpack=True)
  ip = '192.0.43.10'
  print ip2as.get(ip)
