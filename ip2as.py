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
import re


class IP2AS(object):
  def __init__(self, data_path):
    net_as_file = open(data_path, 'rb')
    self.net_as = SubnetTree.SubnetTree()

    for l in net_as_file:
      m = re.match(r'^(\d+)\|([^|]+)\|(.*)$', l)
      if m:
        net = m.group(2)
        text = m.group(1) + '|' + m.group(3)
        self.net_as.insert(net, text)
      else:
        # @TODO what to do if no match
        # should not happen but does happen
        pass

  def get(self, ip):
    try:
      return self.net_as[ip]
    except:
      return ''


if __name__ == '__main__':
  ip2as = IP2AS('net_as')

  print ip2as.get('194.154.205.135')
