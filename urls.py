from django.conf.urls import patterns, url

from loldreams import views

urlpatterns = patterns('',
	url(r'^win_rate', views.win_rate, name='win_rate')
)