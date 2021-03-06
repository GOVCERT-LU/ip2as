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
from ip2as import IP2AS
import ConfigParser


syslog.openlog(os.path.basename(sys.argv[0]), syslog.LOG_PID)
syslog.syslog('starting up')


def parse(fd, out, net_as_path, ttl, domain, lifetime):
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

  ip2as = IP2AS(net_as_path)
  strip_domain = '.' + domain

  syslog.syslog('running')

  count = 0

  while True:
    line = fd.readline().strip()

    if not line:
      syslog.syslog('breaking')
      break

    request = line.split('\t')

    try:
      if len(request) == 6:
        kind, qname, qclass, qtype, qid, ip = request
      else:
        kind, qname, qclass, qtype, qid, ip, their_ip = request
    except:
      print >>out, 'LOG\tPowerDNS sent unparsable line'
      print >>out, 'FAIL'
      out.flush()
      continue

    if qtype in ['TXT', 'ANY'] and qname.endswith(strip_domain):
      q = qname.rstrip(strip_domain)

      try:
        res = ip2as.get(q)

        if res == '':
          raise Exception('Value error')

        answer = 'DATA\t%s\t%s\tTXT\t%d\t-1\t"%s"' % (qname, qclass, ttl, res)
        print >>out, answer
      except:
        pass
    elif qtype in ['SOA'] and qname.endswith(strip_domain):
      q = qname.rstrip(strip_domain)
      res = '{0} hostmaster.{0} 1 60 60 60 60'.format(strip_domain)
      answer = 'DATA\t%s\t%s\tTXT\t%d\t-1\t"%s"' % (qname, qclass, ttl, res)
      print >>out, answer

    print >>out, 'END'
    out.flush()


    if not lifetime == -1:
      count += 1
      if count >= lifetime:
        print >>out, 'FAIL'
        syslog.syslog('Maximum lifetime reached, exiting')
        out.flush()
        sys.exit(-1)

  return 0


if __name__ == '__main__':
  config = ConfigParser.RawConfigParser()
  config.read('/etc/ip2as_pdns.ini')

  try:
    ttl = int(config.get('main', 'ttl'))
    net_as_path = config.get('main', 'net_as_path')
    domain = config.get('main', 'domain')
    lifetime = int(config.get('main', 'lifetime'))
  except ConfigParser.NoOptionError as e:
    print e
    exit(1)

  if net_as_path == '':
    print 'Invalid net_as_path in config file'
    exit(1)

  sys.exit(parse(sys.stdin, sys.stdout, net_as_path, ttl, domain, lifetime))
