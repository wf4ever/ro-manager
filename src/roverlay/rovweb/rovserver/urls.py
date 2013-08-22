from django.conf.urls import patterns, url

from rovserver import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='index')
    url(r'^$', views.RovServerHomeView.as_view(), name='RovServerHomeView'),
    url(r'^ROs/([0-9a-f]{8})/$', views.ResearchObjectView.as_view(), name='ResearchObjectView')
    )
