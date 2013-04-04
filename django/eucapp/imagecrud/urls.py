from django.conf.urls import patterns, url

from imagecrud import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<image_name>\w+)($|/)', views.call, name='image'),
)
