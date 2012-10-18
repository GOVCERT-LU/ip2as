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
from multiprocessing import Pool, Process
import multiprocessing
import re


##############################
# Configuration
debug = True
bview_file_path = 'bview'
ip2as_file_path = 'net_as'
list_as_name_path = 'list_as_name.txt'
rir_data_path = 'delegations'
##############################


# generate cidr net-size
cidr_sizes_4 = {}
for i in range(0, 33):
  net = i
  size = 2 ** (32 - net)

  cidr_sizes_4[str(size)] = str(net)
##############################


def calculate_part_size(file_path):
  """Calculate the chunk size.
     Depending on the CPU cores, this will
     be either 100MB chunks or
     as many as there are cores.

  :param file_path: Path to the file to be parsed.
  :type block: str.
  :returns:  list -- [bview_file_size, part_size]
  """
  # Try to get 100MB parts or as many parts as there are CPU cores
  # @TODO die here if file is 0b
  bview_file_size = os.path.getsize(file_path)
  parts = bview_file_size / 1000 / 1000 / 100

  if parts < multiprocessing.cpu_count():
    parts = multiprocessing.cpu_count()

  part_size = bview_file_size / parts

  return [bview_file_size, part_size]


def get_chunk_end_pos(start_pos, chunk_size, f_file, condition='\n'):
  """Calculate the end position for a give chunk.

  :param start_pos: Where we should start seeking forward.
  :type start_pos: int.
  :param chunk_size: Desired number of chunks.
  :type chunk_size: int.
  :param f_file: file handle
  :type f_file: file.
  :param condition: Stop condition.
  :type condition: str.
  :returns:  int -- The stop position.
  """
  f_file.seek(start_pos, os.SEEK_SET)
  f_file.seek(chunk_size, os.SEEK_CUR)

  while 1:
    l = f_file.readline()

    if not l or not condition or l == condition:
      break

  chunk_pos = f_file.tell()
  f_file.seek(start_pos, os.SEEK_SET)

  return chunk_pos


def split_file(file_path, condition='\n'):
  """Do the file splitting after a specified stop condition.

  :param file_path: The file to be split.
  :type file_path: str.
  :param condition: Stop condition.
  :type condition: str.
  :returns int -- The number of generated chunks.
  """
  start_pos = 0
  f_index = 0
  bview_file_size, part_size = calculate_part_size(file_path)
  bview = open(file_path, 'rb')

  if debug:
    print 'size:', str(bview_file_size)
    print 'part size:', str(part_size)

  while start_pos <= bview_file_size:
    next_pos = get_chunk_end_pos(start_pos, part_size, bview, condition)

    if debug:
      print next_pos

    target = open('target_' + str(f_index), 'wb')

    tmp = bview.read(next_pos - start_pos)
    target.write(tmp)
    target.close()

    start_pos = next_pos
    f_index += 1

  bview.close()

  return f_index
##############################


##############################
# Parse AS name and delegation info
# retrieved from cidr-report
def get_cidrreport_data(file_path):
  """Parse cidr-report data

  :param file_path: The file to be split.
  :type file_path: str.
  :returns list -- [as_names, net_origin_net]
  """
  asnames = open(file_path, 'rb')
  as_names = {}
  net_origin_net = {}
  for l in asnames:
    (net, origin_net, asn, asname) = l.rstrip().split('|')
    as_names[asn] = asname.replace('"', '')
    net_origin_net[net] = origin_net
  asnames.close()

  return [as_names, net_origin_net]
##############################


##############################
# Parse delegation info from RIRs
def parse_rir_data(file_path):
  """Parse RIR data

  :param file_path: The file to be split.
  :type file_path: str.
  :returns list -- Delegations.
  """
  delegations = open(file_path, 'rb')
  delegations_ = {}
  for l in delegations:
    #   afrinic|GH|ipv4|41.57.192.0|16384|20111215|allocated
    try:
      (rir, cc, iptype, net, ipcount,
          changedate, status) = l.rstrip().split('|')

      if not (iptype == 'ipv4' or iptype == 'ipv6'):
        continue

      if not ':' in net:
        net = net + '/' + cidr_sizes_4[ipcount]

      delegations_[net] = cc + '|' + rir + '|' + changedate
    except Exception as e:
      pass
  delegations.close()

  return delegations_
##############################


def parse_block(block):
  """Parse a block from the bview file
     0           1          2 3         4    5          6                                    7   8         9 10 11        12  13
     TABLE_DUMP2|1343808000|B|12.0.1.63|7018|1.0.4.0/22|7018 701 703 38809 56203 56203 56203|IGP|12.0.1.63|0|0 |7018:5000|NAG||

  :param block: Contains one block to parse.
  :type block: str.
  :returns:  list -- [prefix, asn]
  """
  prefix = ''
  asn = ''

  row = block.split('|')

  if row[7] == 'INCOMPLETE' or row[6] == '':
    return None

  if '{' in row[6]:
    asn = row[6].split(' ')[-2]
  else:
    asn = row[6].split(' ')[-1]

  prefix = row[5]

  return [prefix, int(asn)]


def process_chunks(f_name):
  """Spawned as thread using the multiprocessing module.
     Used for parsing a chunk of the bview file.

  :param f_name: Chunk file name.
  :type f_name: str.
  :returns:  dict -- maps nets to AS numbers
  """

  if debug:
    print f_name

  f = open(f_name, 'rb')

  net_as = {}
  inblock = False
  block = ''

  try:
    for l in f:
      l = l.rstrip()

      res = parse_block(l)
      if not res:
        continue
      prefix, asn = res

      if not prefix or prefix == '0.0.0.0/0':
        continue

      if not prefix in net_as:
        net_as[prefix] = asn
  except Exception as e:
    import sys
    import traceback
    print >> sys.stderr , 'EXCEPTION OCCURED: %s' % e
    traceback.print_tb(sys.exc_traceback)

  f.close()

  return net_as


def combine_dict(dict1, dict2):
  """This functions merges dict2 into dict1.

  :param dict1: Target dictionary.
  :type dict1: dict.
  :param dict2: Source dictionary.
  :type dict2: dict.
  :returns:  None
  """
  for k, v in dict2.items():
    if not k in dict1:
      dict1[k] = v
    else:
      dict1[k] += v


if __name__ == '__main__':
  #if debug:
  #  file_chunks = 10
  #else:
  #file_chunks = split_file(bview_file_path)
  file_chunks = split_file(bview_file_path, None)

  as_names, net_origin_net = get_cidrreport_data(list_as_name_path)
  delegations = parse_rir_data(rir_data_path)

  # Setup process pool and submit jobs for processing
  pool = Pool()
  results = []

  for i in range(0, file_chunks):
    result = pool.apply_async(process_chunks, ['target_' + str(i)])
    results.append(result)

  pool.close()
  pool.join()
  ##############################

  # Get results from jobs and combine into a single dictionary
  net_as = {}

  for k in results:
    net_as1 = k.get()
    combine_dict(net_as, net_as1)
  ##############################

  # Combine bview information with that found in
  # the data from the RIRs and cidr-report.
  # Write the result to a file.
  out = open(ip2as_file_path, 'wb')
  for net, asn in net_as.items():
    if str(asn) in as_names:
      name = as_names[str(asn)]
    else:
      name = ''

    try:
      if net in delegations:
        moreinfo = '|' + delegations[net]
      elif net in net_origin_net and net_origin_net[net] in delegations:
        moreinfo = '|' + delegations[net_origin_net[net]]
      else:
        moreinfo = '|||'
    except Exception as e:
      if debug:
        print 'Exception while parsing', net
        print e
        print
      moreinfo = ''

    out.write(str(asn) + '|' + str(net) + '|' + name + moreinfo + '\n')
  out.close()
  ##############################

  if debug:
    print 'prefixes:', len(net_as.keys())
