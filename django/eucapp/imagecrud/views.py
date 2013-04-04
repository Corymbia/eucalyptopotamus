from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from imagecrud.models import Image
from django import forms
import base64
import os

from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

# Create your views here.
def index(request):
    body=''
    try:
        for image in Image.objects.all():
            body = body + 'http://%s%s%s\n' % (request.get_host(), request.get_full_path(), image.name)
    except Exception, err:
        return HttpResponse(err, status=500)
 
    return HttpResponse(body, status=200)

img_dir = '/tmp/image_crud/'

def store_uploaded_file(f, name):
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    path = '%s%s' % (img_dir,name)
    with open(path , 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path

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
    except:
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
    
    data = None
    try:
       file = open(path)
       data = file.read()
       file.close()
    except Exception, err:
        return HttpResponse(err, status=500)
    try:
        encoded = base64.b64encode(data)
        type='jpeg'
        if path.endswith('jpg') or path.endswith('jpeg') or path.endswith('JPG') or path.endswith('JPEG'):
            type='jpeg'
        elif path.endswith('gif') or path.endswith('GIF'):
            type='gif'
        body = '<html><head></head><body> <img src=\"data:image/%s;base64,%s\"> </body></html>' % (type,encoded)
        return HttpResponse(body, status=200)
    except Exception, err:
        return HttpResponse(err, status=500)


def delete(request, image_name):
    try:
        image=Image.objects.get(name=image_name)
        filepath = image.path
        print "deleting: %s" %filepath
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except Exception, err:
            return HttpResponse(err, status=500)
        image.delete()
        return HttpResponse(status=200)
    except Image.DoesNotExist:
        return HttpResponse(status=404)
    except Exception, err:
        return HttpResponse(status=500)
