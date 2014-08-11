from django.core.management.base import BaseCommand, CommandError
from loldreams.models import *
from django.conf import settings

import urllib2
import json

API_BASE_URL = 'https://na.api.pvp.net/api/lol'

#Gets a list of all champions, puts them into the database
class Command(BaseCommand):
	help = 'Get new list of champoins.'

	def handle(self, *args, **options):
		self.stdout.write('Updating the list of champions...')

		url = API_BASE_URL + '/static-data/na/v1.2/champion?api_key=' + settings.RIOT_API_KEY
		self.stdout.write( 'Querying ' + url )
		response = json.loads( urllib2.urlopen(url).read() )

		for key, champion in response['data'].iteritems():
			if len( Champion.objects.filter(riotid=champion['id']) ) == 0:
				champ = Champion( name = champion['name'], key = champion['key'], riotid = champion['id'] )
				champ.save()
				self.stdout.write( champion['name'] + ' entry created.' )
			else:
				self.stdout.write( champion['name'] + ' already exists.' )
