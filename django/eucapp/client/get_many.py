#!/usr/bin/python

import os, sys
from optparse import OptionParser
import commands
from random import randrange
if __name__ == "__main__":
    parser = OptionParser(usage='Usage: %prog url')
    parser.add_option("-c", "--count", help="Number of files to get", action="store", default=1, dest="count")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_usage()
        sys.exit(1)

    url = args[0]
    count = int(options.count)

    output = commands.getoutput('curl %s' % url)
    lines = output.split('\n')
    files = []
    for line in lines:
        if line.startswith('http'):
            files.append(line)

    if len(files) <= 0:
        print "No files found"
        sys.exit(1)

    for i in range(0, count):
        idx = randrange(0, len(files))
        url = files[idx]
        output = commands.getoutput('curl %s ' % url)     
        print 'read %d/%d' % (i, count)
