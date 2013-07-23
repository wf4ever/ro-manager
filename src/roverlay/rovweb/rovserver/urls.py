from django.conf.urls import patterns, url

from rovserver import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='index')
    url('^$', views.RovServerHomeView.as_view(), name='RovServerHomeView')
    )
