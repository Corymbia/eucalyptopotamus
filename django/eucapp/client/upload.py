#!/usr/bin/python

import os, sys
import pycurl
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser(usage='Usage: %prog file url')
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_usage()
        sys.exit(1)

    filepath = args[0]
    url = args[1]
    if not os.path.exists(filepath):
        print "can't find %s in the filesystem" % filepath
        sys.exit(1)

    c = pycurl.Curl()
    c.setopt(c.POST, 1)
    c.setopt(c.URL, url)
    c.setopt(c.HTTPPOST, [("file", (c.FORM_FILE, filepath))])
    c.perform()
    if c.getinfo(pycurl.HTTP_CODE) == 200:
        print "\nFile successfully uploaded"
    else:
	print "\nFailed to upload: %d" % c.getinfo(pycurl.HTTP_CODE)

    c.close()

