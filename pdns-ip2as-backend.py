#!/usr/bin/python

# -*- coding: utf-8 -*-

# This file is part of ip2as.
#
# PDNS pipe-backend inspired by:
# http://pdns-dynamic-reverse-backend.googlecode.com
# Copyright (c) 2009 Wijnand "maze" Modderman
# Copyright (c) 2010 Stefan "ZaphodB" Schmidt
#
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


import sys
import traceback
import os
import re
import syslog
import time
import SubnetTree


########################################
# Configuration
net_as_path = '/log/bview_foo/net_as'
########################################


syslog.openlog(os.path.basename(sys.argv[0]), syslog.LOG_PID)
syslog.syslog('starting up')


def parse(fd, out):
  line = fd.readline().strip()
  if not line.startswith('HELO'):
      syslog.syslog('FAIL')
      print >>out, 'FAIL'
      out.flush()
      syslog.syslog('received "%s", expected "HELO"' % (line,))
      sys.exit(1)
  else:
    print >>out, 'OK\t%s ready' % (os.path.basename(sys.argv[0]),)
    out.flush()
    syslog.syslog('received HELO from PowerDNS')

  net_as = open(net_as_path, 'rb')
  t1 = SubnetTree.SubnetTree()

  for l in net_as:
    try:
      (asn, net, asname, cc, rir, changedate) = l.rstrip().split('|')
      text = asn + ' | ' + net + ' | ' + asname + ' | ' + cc + ' | ' + rir + ' | ' + changedate
    except:
      (asn, net, asname) = l.rstrip().split('|')
      text = asn + ' | ' + net + ' | ' + asname

    t1.insert(net, text)

  syslog.syslog('running')

  lastnet = 0
  while True:
    line = fd.readline().strip()
    if not line:
      break

    request = line.split('\t')

    if len(request) < 6:
      print >>out, 'LOG\tPowerDNS sent unparsable line'
      print >>out, 'FAIL'
      out.flush()
      continue

    try:
      kind, qname, qclass, qtype, qid, ip = request
    except:
      kind, qname, qclass, qtype, qid, ip, their_ip = request

    if qtype in ['TXT', 'ANY'] and qname.endswith('-ip2as'):
      q = qname.rstrip('-ip2as')

      try:
        if t1 and t1[q]:
          reply = t1[q]
          answer = 'DATA\t%s\t%s\tTXT\t%d\t-1\t"%s"' % (qname, qclass, 300, reply)
          print >>out, answer
      except:
        pass

    print >>out, 'END'
    out.flush()

  return 0


if __name__ == '__main__':
    sys.exit(parse(sys.stdin, sys.stdout))
