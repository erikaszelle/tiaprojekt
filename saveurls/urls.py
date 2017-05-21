"""saveurls URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from main import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^register/$', views.register),
    url(r'^category/(?P<id>[0-9]+)/$', views.view_category, name='view_category'),
    url(r'^category/all/$', views.view_all_categories, name='view_all_categories'),
    url(r'^category/add/$', views.add_category, name='add_category'),
    url(r'^category/delete/(?P<id>[0-9]+)/$', views.delete_category, name='delete_category'),
    url(r'^url/add/$', views.add_url, name='add_url'),
    url(r'^url/delete/(?P<id>[0-9]+)/$', views.delete_url, name='delete_url'),
    url(r'^url/edit/(?P<id>[0-9]+)/$', views.edit_url, name='edit_url'),
    url(r'^label/add/(?P<id>[0-9]+)/$', views.add_label, name='add_label'),
    url(r'^search/$', views.search, name='search'),
    url(r'^label/search/(?P<id>[0-9]+)/$', views.search_label, name='search_label'),
    url(r'^label/delete/(?P<url_id>[0-9]+)/(?P<label_id>[0-9]+)/$', views.delete_label, name='delete_label'),
]
