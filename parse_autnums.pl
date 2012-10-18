#!/usr/bin/perl

while (<STDIN>)
{
  # <a href="/cgi-bin/as-report?as=AS21&view=(null)">AS21   </a> RAND - The RAND Corporation
  # <a href="/cgi-bin/as-report?as=AS327706&view=(null)">AS5.26</a> ISPA-SA-CINX

  if (/>AS([^\s]+)\s*<\/a>\s*(.*)/)
  {
    print "$1|$2\n";
  }else{
    #print $_;
  }
}
