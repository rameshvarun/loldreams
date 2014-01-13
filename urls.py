from django.conf.urls import patterns, url

from loldreams import views

urlpatterns = patterns('',
	url(r'^$', views.home, name='home'),
	url(r'^winrate', views.winrate, name='winrate'),
	url(r'^reccomendations', views.reccomendations, name='reccomendations'),
	#url(r'^(?P<page_name>[a-zA-Z0-9_.-/]+)', views.page, name='page')
)