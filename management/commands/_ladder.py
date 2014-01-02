from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from loldreams.models import *

from HTMLParser import HTMLParser
from django.core.cache import cache

import urllib2
import urllib
import time
import json
import cPickle

API_BASE_URL = 'https://prod.api.pvp.net/api/lol'

LADDER_URLS = {
	CHALLENGER : ['http://www.lolsummoners.com/leagues/challenger/solo/REGION'],
	DIAMONDI : ['http://www.lolsummoners.com/leagues/solo/REGION/Diamond/Varus%27s%20Warmongers/I', 'http://www.lolsummoners.com/leagues/solo/REGION/Diamond/Zilean%27s%20Urfriders/I']
}

#Parsing class for parsing lolsummoner.com
class LadderParser(HTMLParser):
	def __init__(self, out):
		self.out = out
		self.tags = [] #A stack of tags, to help search for patterns
		
		self.summoner_ids = []
		
		HTMLParser.__init__(self)
		
	def handle_starttag(self, tag, attrs):
		element = dict(attrs)
		element['tagName'] = tag
		self.tags.insert(0, element)
		try:
			if self.tags[0]['tagName'] == 'a': #An <a>
				if self.tags[1]['tagName'] == 'td':	#Within a <td>
					if self.tags[2]['tagName'] == 'tr':	#Within a <tr>
						self.summoner_ids.append( self.tags[0]['href'].split('/')[-1] )
		except:
			pass
	def handle_endtag(self, tag):
		element = self.tags.pop(0)
		
	def handle_data(self, data):
		pass
			
CACHE_LADDER_TIME = 60 * 60 * 24 * 3 #Cache ladder for three days

#Given a region and a tier, returns all summoners in the tier
def GetSummonersInTier(out, region, tier):
	hash = region + str(tier)
	
	if hash in cache:
		summoner_ids = cache.get(hash)
		print "\t\t", len(summoner_ids), " total"
		return summoner_ids
	
	summoner_ids = []
	for url in LADDER_URLS[tier]:
		new_url = url.replace('REGION', region)
		out.write("\t\t\t" + new_url)
		
		parser = LadderParser(out)
		parser.feed( urllib2.urlopen(new_url).read() )
		time.sleep(1)
		
		print "\t\t\t", len(parser.summoner_ids), " summoners found."
		summoner_ids.extend( parser.summoner_ids )
		
	print "\t\t", len(summoner_ids), " total"
	cache.set(hash, summoner_ids, CACHE_LADDER_TIME)
	return summoner_ids