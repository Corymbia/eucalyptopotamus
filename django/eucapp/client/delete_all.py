#!/usr/bin/python

import os, sys
from optparse import OptionParser
import commands

if __name__ == "__main__":
    parser = OptionParser(usage='Usage: %prog url')
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_usage()
        sys.exit(1)

    url = args[0]
    output = commands.getoutput('curl %s' % url)
    lines = output.split('<a href=')
    for line in lines:
       try:
           idx_start = line.index('"')+1
           idx_end = line.index('>')
           img_url = '%s%s' % (url,line[idx_start:idx_end-1])
           commands.getoutput('./delete.py %s' % img_url)
           print 'deleted %s' % img_url
       except Exception, err:
           pass
