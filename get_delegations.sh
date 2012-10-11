#!/bin/bash

wget -O - ftp://ftp.arin.net/pub/stats/arin/delegated-arin-latest \
          ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest \
          ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest \
          ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest \
          ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest \
          > delegations
