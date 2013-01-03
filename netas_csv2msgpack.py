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


import mmap
try:
  import msgpack
except:
  print '  -> msgpack not installed, skipping msgpack creation'
  exit(1)


def parse_line(ip2as_line):
  asn, net, descr, cc, rir, update = ip2as_line.split('|')

  if update == '':
    update = 0
  else:
    update = int(update)

  # a: asn, n: net, d: descr, c: cc, r: rir, u: update
  return {'a' : asn, 'n' : net, 'd' : descr, 'c' : cc,
          'r' : rir, 'u' : update}


if __name__ == '__main__':
  data_path = 'net_as'

  net_as_file = open(data_path, 'rb')
  net_as_mmap = mmap.mmap(net_as_file.fileno(), 0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)

  ip2as_list = []

  for l in iter(net_as_mmap.readline, ''):
    try:
      ipdescr = parse_line(l[:-1])
      ip2as_list.append(ipdescr)
    except Exception as e:
      # @TODO what to do if no match
      # should not happen but does happen
      print e
      pass

  net_as_mmap.close()
  net_as_file.close()

  net_as_bin = open(data_path + '.bin', 'wb')
  msg = msgpack.packb(ip2as_list)
  net_as_bin.write(msg)
  net_as_bin.close()
