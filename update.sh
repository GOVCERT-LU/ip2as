#!/bin/bash

MAXDIFF=15


# compare percentage difference of two files
compare_files()
{
  file1=$1
  file2=$2
  maxdiff=$3

  file1_size=`stat -c %s $file1`
  file2_size=`stat -c %s $file2`

  if [[ $file1_size -gt $file2_size ]]
  then
    perc=`echo "scale=20; (100 - ((100 / $file1_size) * $file2_size))" | bc`
    perc=${perc/\.*}
  else
    perc=`echo "scale=20; (100 - ((100 / $file2_size) * $file1_size))" | bc`
    perc=${perc/\.*}
  fi

  if [[ $perc -gt $maxdiff ]]
  then
    return 1
  else
    return 0
  fi
}




# Generate msprefix list
wget -O - http://www.cidr-report.org/as2.0/msprefix-list.html | perl parse_msprefix.pl | sort | uniq > list_as_name.txt_new

if ! compare_files list_as_name.txt list_as_name.txt_new $MAXDIFF
then
  echo "Too many changes for AS/Name DB ... exiting"
  exit 1
else
  mv list_as_name.txt_new list_as_name.txt
fi


# Generate AS/Name DB
wget -O - http://www.cidr-report.org/as2.0/autnums.html | perl parse_autnums.pl > list_autnums.txt_new

if ! compare_files list_autnums.txt list_autnums.txt_new $MAXDIFF
then
  echo "Too many changes for AS/Name DB ... exiting"
  exit 1
else
  mv list_autnums.txt_new list_autnums.txt
fi


# Get latest bview DB
wget -O - http://data.ris.ripe.net/rrc00/latest-bview.gz | zcat -dc | bgpdump -v -m - > bview_new

if ! compare_files bview bview_new $MAXDIFF
then
  echo "Too many changes for bview ... exiting"
  exit 1
else
  mv bview_new bview
fi


# Get latest delegations from RIRs
wget -O - ftp://ftp.arin.net/pub/stats/arin/delegated-arin-latest \
          ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest \
          ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest \
          ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest \
          ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest \
          > delegations_new

if ! compare_files delegations delegations_new $MAXDIFF
then
  echo "Too many changes for RIRs delegation file ... exiting"
  exit 1
else
  mv delegations_new delegations
fi


# Parse it all
pypy bview2asnet.py



exit 0
