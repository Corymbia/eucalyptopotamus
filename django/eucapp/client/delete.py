#!/usr/bin/python

import os, sys
import pycurl
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser(usage='Usage: %prog url')
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_usage()
        sys.exit(1)

    url = args[0]

    c = pycurl.Curl()
    c.setopt(c.CUSTOMREQUEST, 'DELETE')
    c.setopt(c.URL, url)
    c.perform()
    if c.getinfo(pycurl.HTTP_CODE) == 200:
        print "\nFile successfully deleted"
    else:
	print "\nFailed to delete: %d" % c.getinfo(pycurl.HTTP_CODE)
    c.close()

