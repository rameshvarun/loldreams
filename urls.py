from django.conf.urls import patterns, url

from loldreams import views

urlpatterns = patterns('',
	url(r'^$', views.home, name='home'),
	url(r'^win_rate', views.win_rate, name='win_rate'),
	url(r'^reccomendations', views.reccomendations, name='reccomendations'),
	url(r'^rankings', views.champion_rankings, name='champion_rankings'),
	#url(r'^(?P<page_name>[a-zA-Z0-9_.-/]+)', views.page, name='page')
)