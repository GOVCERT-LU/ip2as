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


import os
import json
from ip2as.asn import ASN


##############################
# Configuration
debug = True
bview_file_path = 'bview'
ip2as_file_path = 'net_as_new'
list_msprefix_path = 'list_as_name.txt'
list_autnums_path = 'list_autnums.txt'
rir_data_path = 'delegations'
##############################


# generate cidr net-size
cidr_sizes_4 = {}
for i in range(0, 33):
  net = i
  size = 2 ** (32 - net)

  cidr_sizes_4[str(size)] = str(net)
##############################


def get_cidrreport_data(msprefix_path, autnums_path):
  '''
  Parse AS name and delegation info
  retrieved from cidr-report

  :param msprefix_path: msprefix list.
  :param autnums_path: autnums list.
  :type file_path: str.
  :returns list -- [as_names, net_origin_net]
  '''
  asnames = open(msprefix_path, 'rb')
  as_names = {}
  net_origin_net = {}
  for l in asnames:
    (net, origin_net, asn, asname) = l.rstrip().split('|')
    asname = asname.replace('"', '')

    try:
      asname = unicode(asname, 'utf-8')
    except UnicodeDecodeError:
      try:
        asname = unicode(asname, 'latin-1')
      except UnicodeDecodeError:
        asname = asname.decode('utf-8', 'ignore')

    as_names[asn] = asname
    net_origin_net[net] = origin_net

  asnames.close()

  asnames = open(autnums_path, 'rb')
  for l in asnames:
    (asn, asname) = l.rstrip().split('|')
    asname = asname.replace('"', '')

    try:
      asname = unicode(asname, 'utf-8')
    except UnicodeDecodeError:
      try:
        asname = unicode(asname, 'latin-1')
      except UnicodeDecodeError:
        asname = asname.decode('utf-8', 'ignore')

    as_names[asn] = asname

  asnames.close()

  return [as_names, net_origin_net]


def parse_rir_data(file_path):
  '''Parse RIR data

  :param file_path: The file to be split.
  :type file_path: str.
  :returns list -- Delegations.
  '''
  delegations = open(file_path, 'rb')
  ip_del = {}
  as_del = {}
  for l in delegations:
    #   arin   |US|asn |20         |1    |19840727|allocated
    #   afrinic|GH|ipv4|41.57.192.0|16384|20111215|allocated
    try:
      (rir, cc, iptype, net, ipcount,
          changedate, status) = l.rstrip().split('|')

      if iptype == 'ipv4' or iptype == 'ipv6':
        if not ':' in net:
          net = net + '/' + cidr_sizes_4[ipcount]

        ip_del[net] = {'cc': cc, 'rir': rir, 'timestamp': changedate}
      elif iptype == 'asn':
        as_del[net] = {'cc': cc, 'rir': rir, 'timestamp': changedate}
    except Exception as e:
      #print e
      pass
  delegations.close()

  return ip_del, as_del


def parse_block(block):
  '''Parse a block from the bview file
     0           1          2 3         4    5          6                                    7   8         9 10 11        12  13
     TABLE_DUMP2|1343808000|B|12.0.1.63|7018|1.0.4.0/22|7018 701 703 38809 56203 56203 56203|IGP|12.0.1.63|0|0 |7018:5000|NAG||

  :param block: Contains one block to parse.
  :type block: str.
  :returns:  list -- [prefix, asn]
  '''
  prefix = ''
  asn = ''

  row = block.split('|')

  if row[7] == 'INCOMPLETE' or row[6] == '':
    raise ValueError('data incomplete')

  if '{' in row[6]:
    asn = row[6].split(' ')[-2]
  else:
    asn = row[6].split(' ')[-1]

  prefix = row[5]

  return [prefix, asn]


if __name__ == '__main__':
  bview = open(bview_file_path, 'rb')
  d_asn = {}

  for l in bview:
    try:
      net, asn = parse_block(l)
    except ValueError:
      continue

    if net == '0.0.0.0/0':
      continue

    if not asn in d_asn:
      d_asn[asn] = ASN(asn)

    d_asn[asn].nets[net] = {'cc': '', 'rir': '', 'timestamp': ''}

  as_names, net_origin_net = get_cidrreport_data(list_msprefix_path, list_autnums_path)
  ip_del, as_del = parse_rir_data(rir_data_path)

  for asn, v in d_asn.items():
    if asn in as_del:
      v.rir = as_del[asn]['rir']
      v.cc = as_del[asn]['cc']
      v.timestamp = as_del[asn]['timestamp']

    if asn in as_names:
      v.name = as_names[asn]

    for net in v.nets.keys():
      if net in ip_del:
        v.nets[net] = ip_del[net]
      elif net in net_origin_net and net_origin_net[net] in ip_del:
        v.nets[net] = ip_del[net_origin_net[net]]

  export_asn = {}
  for k, v in d_asn.items():
    export_asn[k] = v.todict()

  # json export
  f = open(ip2as_file_path, 'wb')
  f.write(json.dumps(export_asn))
  f.close()


  # msgpack export
  try:
    import msgpack

    f = open(ip2as_file_path + '_msgpack', 'wb')
    f.write(msgpack.packb(export_asn))
    f.close()
  except:
    # ignore
    pass
