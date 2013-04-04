#!/usr/bin/python

import os, sys
import pycurl
from optparse import OptionParser
from random import randrange
import commands

if __name__ == "__main__":
    parser = OptionParser(usage='Usage: %prog directory url') 
    parser.add_option("-c", "--count", help="Number of files to upload", action="store", default=1, dest="count")
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_usage()
        sys.exit(1)

    dir = args[0]
    if not dir.endswith('/'):
        dir = dir+'/'

    url = args[1]
    if not url.endswith('/'):
        url = url+'/'

    if not os.path.exists(dir):
        parser.print_usage()
        sys.exit(1)

    files = os.listdir(dir)
    count = int(options.count)
    for i in range(0, count):
       ridx = randrange(0, len(files)-1) 
       path = dir+files[ridx]
       name = os.urandom(8).encode('hex') 
       target_url = url + name
       print '%s-%s' %(path, target_url)   
       out = commands.getoutput("./upload.py %s %s" % (path, target_url))
