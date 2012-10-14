#!/bin/bash

wget -c http://data.ris.ripe.net/rrc00/latest-bview.gz
gunzip latest-bview.gz
bgpdump latest-bview > bview
