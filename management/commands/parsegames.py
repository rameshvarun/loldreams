from django.core.management.base import BaseCommand, CommandError
from loldreams.models import *

from HTMLParser import HTMLParser

import urllib2

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
		page += 1

class Command(BaseCommand):
	help = 'Populate the database with parsed games from the API'
	
	def handle(self, *args, **options):
		summoner_names = GetSummonersInTier(self.stdout, "na", "Challenger")