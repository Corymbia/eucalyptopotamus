import boto
import boto.s3.connection
import string
import random

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

calling_format=boto.s3.connection.OrdinaryCallingFormat()
connection = boto.s3.connection.S3Connection(aws_access_key_id='4JWDSSAGCE4VSC5WPC0GV',
                      aws_secret_access_key='b0PGLn36sHePTU8Mwru2X9KU5B8qnGRH5UCTDjvV',
                      is_secure=False,
                      host='192.168.51.170',
                      port=8773,
                      calling_format=calling_format,
                      path="/services/Walrus")

#Run commands

try:
    bucket = connection.get_bucket('imagecrud')
except:
    bucket = connection.create_bucket('imagecrud')

key_name=id_generator()

print "adding a new key %s" % key_name
key = bucket.new_key(key_name)
key.set_contents_from_string('Hello World!')
key.set_canned_acl('public-read')

print "getting key contents to file"
for k in bucket.list():
    k.get_contents_to_filename('/tmp/%s'% k.key)
    print "content stored in %s" % k.key
