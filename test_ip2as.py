from ip2as import IP2AS


if __name__ == '__main__':
  ip2as = IP2AS('net_as')

  ips_file = open('test_ips', 'rb')
  ips = []

  for i in ips_file:
    ips.append(i.rstrip())

  from time import time
  t1 = time()

  for i in ips:
    print ip2as.get(i)

  t2 = time() - t1
  print t2
