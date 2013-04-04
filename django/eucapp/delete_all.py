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
    lines = output.split('\n')
    for line in lines:
        if line.startswith('http'):
            commands.getoutput('./delete.py %s' % line)
