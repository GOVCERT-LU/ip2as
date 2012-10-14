#!/bin/bash

wget -O - http://www.cidr-report.org/as2.0/msprefix-list.html | ./parse_msprefix.pl | sort | uniq > list_as_name.txt
