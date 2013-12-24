from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from loldreams.models import *

from HTMLParser import HTMLParser

import urllib2
import urllib
import time
import shelve
import json

API_BASE_URL = 'https://prod.api.pvp.net/api/lol'

class LadderParser(HTMLParser):
	def __init__(self, out):
		self.out = out
		self.tags = [] #A stack of tags, to help search for patterns
		
		self.summoners = []
		self.currentSummoner = []
		
		HTMLParser.__init__(self)
		
	def handle_starttag(self, tag, attrs):
		element = dict(attrs)
		element['tagName'] = tag
		self.tags.insert(0, element)
		
		if element['tagName'] == 'tr' and 'class' in element and element['class'] == 'row1':
			self.currentSummoner = []
	def handle_endtag(self, tag):
		element = self.tags.pop(0)
		
		if element['tagName'] == 'tr' and 'class' in element and element['class'] == 'row1':
			self.summoners.append( { 
				'name' : self.currentSummoner[1],
				'tier' : self.currentSummoner[2]
				} )
	def handle_data(self, data):
		if data.strip():
			self.currentSummoner.append(data.strip())
			
def GetSummonersInTier(out, region, tier):
	summoners = []
	out.write('Getting a list of all summoner names in tier ' + tier + ' and region ' + region)
	
	page = 1
	tierStarted = False
	while True:
		out.write('Page ' + str(page))
		
		url = 'http://www.lolsummoners.com/ladder/' + region + '/' + str(page)
		parser = LadderParser(out)
		parser.feed( urllib2.urlopen(url).read() )
		
		for summoner in parser.summoners:
			if summoner['tier'].lower() == tier.lower():
				tierStarted = True
				summoners.append( summoner['name'] )
			else:
				if tierStarted:
					out.write(str(len(summoners)) + " summoners found.")
					return summoners
					
		time.sleep(1)
		page += 1
		
def GetSummonerProfileByName(name, region):
	time.sleep(1)
	url = API_BASE_URL + '/' + region + '/v1.1/summoner/by-name/' + urllib.quote( name ) + '?api_key=' + settings.RIOT_API_KEY
	print url
	return json.loads( urllib2.urlopen(url).read() )
			
class Command(BaseCommand):
	help = 'Update the stored challenger ladder.'
	
	def handle(self, *args, **options):
		#Store the ladder data in a python 'shelf'
		shelf = shelve.open("ladder.cache")
		
		for region_code, region_name in REGION_CHOICES:
			shelf[ region_code + '_challenger_names'] = GetSummonersInTier(self.stdout, region_code, "Challenger")
			shelf.sync()
			
			shelf[ region_code + '_challenger_ids' ] = [ GetSummonerProfileByName(name, region_code)['id'] for name in shelf[ region_code + '_challenger_names']]
			shelf.sync()
		
		shelf.close()