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


from optparse import OptionParser
from random import randint


def genIP():
  ip = ''

  for i in range (0,4):
    rnd = randint(1, 254)

    if not ip == '':
      ip += '.'

    ip += str(rnd)

  return ip


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-c", dest="howmany",
                  help="how many IPs you want to generate")

  (options, args) = parser.parse_args()

  if not options.howmany:
    parser.print_help()
    exit(1)

  ips = []
  c = 0

  while c < int(options.howmany):
    ip = genIP()
    if not ip in ips:
      ips.append(ip)
      c += 1

  for i in ips:
    print i
