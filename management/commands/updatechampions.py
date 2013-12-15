from django.core.management.base import BaseCommand, CommandError
from loldreams.models import *
from django.conf import settings

import urllib2
import json

API_BASE_URL = 'https://prod.api.pvp.net/api/lol'

class Command(BaseCommand):
	help = 'Get new list of champoins.'
	
	def handle(self, *args, **options):
		self.stdout.write('Updating the list of champions...')
		
		url = API_BASE_URL + '/na/v1.1/champion?api_key=' + settings.RIOT_API_KEY
		self.stdout.write( 'Querying ' + url )
		response = json.loads( urllib2.urlopen(url).read() )
		
		for champion in response['champions']:
			if len( Champion.objects.filter(riotid=champion['id']) ) == 0:
				champ = Champion( name = champion['name'], riotid = champion['id'] )
				champ.save()
				self.stdout.write( champion['name'] + ' entry created.' )
			else:
				self.stdout.write( champion['name'] + ' already exists.' )