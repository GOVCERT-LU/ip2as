#!/usr/bin/perl

while (<STDIN>)
{
  #    12.139.84.0/24       (12.0.0.0/8)         AS2386  INS-AS - AT&T Data Communications Services

  if (/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\s+\((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\)\s+AS(\d+)\s+(.*)/)
  {
    print "$1|$2|$3|$4\n";
  }
}
