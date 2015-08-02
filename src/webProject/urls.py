from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webProject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'CoDEX.views.home'),
    url(r'^', include('CoDEX.urls')),
    url(r'^CoDEX/', include('CoDEX.urls')),
)
