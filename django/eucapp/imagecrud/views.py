from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from imagecrud.models import Image
from django import forms
import base64
import os
import boto
import boto.s3.connection
import string
import random
import httplib2
from django import forms

service_path= 'imagecrud/'
img_bucket = 'image_crud'
access_key = '4JWDSSAGCE4VSC5WPC0GV'
secret_key = 'b0PGLn36sHePTU8Mwru2X9KU5B8qnGRH5UCTDjvV'
s3_host = '192.168.51.170'
s3_port = 8773
s3_path = '/services/Walrus'


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

ip_address = None

def get_ipaddr():
    try:
        if ip_address is None:
            resp, content = httplib2.Http().request("http://169.254.169.254/latest/meta-data/hostname")
        else:
            return ip_address
        if resp['status'] != '200' or len(content) <= 0:
            return '127.0.0.1'
        else:
            ip_address = content
            return ip_address
    except Exception, err:
        return '127.0.0.1'
 
# Create your views here.
def index(request):
    body='<html> <head> </head> <body> <table>'
    num_col=8
    try:
        i = 0
        for image in Image.objects.all():
            if i % num_col == 0:
                body = body + '<tr>'
            url = '%s' % image.name
            body = body + '<td> <a href="%s"> <img src="%s" width=100/> </a> </td>' % (url,image.path) 
            if i % num_col == num_col:
                body = body + '</tr>'
            i=i+1
        body = body + '</table> </body> </html>'
    except Exception, err:
        return HttpResponse(err, status=500)
 
    return HttpResponse(body, status=200)


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def store_uploaded_file(f, name):
    img_dir='/tmp/image/'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    file_name = id_generator()
    path = '%s%s' % (img_dir,file_name)
    with open(path , 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    calling_format=boto.s3.connection.OrdinaryCallingFormat()
    connection = boto.s3.connection.S3Connection(aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key,
                      is_secure=False,
                      host=s3_host,
                      port=s3_port,
                      calling_format=calling_format,
                      path=s3_path)

    try:
        bucket = connection.get_bucket(img_bucket)
    except:
        bucket = connection.create_bucket(img_bucket)

    key_name= '%s.jpg' % id_generator()
    key = bucket.new_key(key_name)
    key.set_contents_from_filename(path)
    key.set_canned_acl('public-read')
    key.close()

    return 'http://%s:%s%s/%s/%s' % (s3_host, s3_port,s3_path,img_bucket,key_name)

@csrf_exempt
def call(request, image_name):
    if request.method == 'POST':
        return update(request, image_name)
    elif request.method == 'GET':
        return read(request, image_name)
    elif request.method == 'DELETE':
        return delete(request, image_name)

def update(request, image_name):
    form = UploadFileForm(request.GET, request.FILES)
    path = None
    try:
        path= store_uploaded_file(request.FILES['file'], image_name)
    except Exception, err:
        print "error: %s" % err
        return HttpResponse('server error', status=500)
    try:
        image=Image.objects.get(name=image_name)
        image.pub_date=timezone.now()
        image.save()
        return HttpResponse(status=200)
    except Image.DoesNotExist:
        img = Image(name=image_name,pub_date=timezone.now(),path=path)
        img.save()
        return HttpResponse(status=200)

def read(request, image_name):
    path = None
    try:
        image=Image.objects.get(name=image_name)
        path = image.path
    except Image.DoesNotExist:
        return HttpResponse(status=404)
    try:
        body = '<html><head></head><body> <img src="%s"> </body></html>' % path
        return HttpResponse(body, status=200)
    except Exception, err:
        return HttpResponse(err, status=500)


def delete(request, image_name):
    try:
        image=Image.objects.get(name=image_name)
        path = image.path
        token = path.split('/')
        key_name = token[len(token)-1]
        try:
            calling_format=boto.s3.connection.OrdinaryCallingFormat()
            connection = boto.s3.connection.S3Connection(aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key,
                      is_secure=False,
                      host=s3_host,
                      port=s3_port,
                      calling_format=calling_format,
                      path=s3_path)

            bucket = connection.get_bucket(img_bucket)
            bucket.delete_key(key_name)
        except Exception, err:
            return HttpResponse(err, status=500)
        image.delete()
        return HttpResponse(status=200)
    except Image.DoesNotExist:
        return HttpResponse(status=404)
    except Exception, err:
        return HttpResponse(status=500)
