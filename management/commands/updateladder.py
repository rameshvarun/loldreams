from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from loldreams.models import *

from HTMLParser import HTMLParser

import urllib2
import urllib
import time
import json
import cPickle

API_BASE_URL = 'https://prod.api.pvp.net/api/lol'

LADDER_URLS = {
	CHALLENGER : ['http://www.lolsummoners.com/leagues/challenger/solo/REGION'],
	DIAMONDI : ['http://www.lolsummoners.com/leagues/solo/REGION/Diamond/Taric%27s%20Shadehunters/I']
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
			
#Given a region and a tier, returns all summoners in the tier
def GetSummonersInTier(out, region, tier):
	for url in LADDER_URLS[tier]:
		new_url = url.replace('REGION', region)
		out.write("\t\t" + new_url)
		
		parser = LadderParser(out)
		parser.feed( urllib2.urlopen(new_url).read() )
		time.sleep(1)
		
		print "\t\t", len(parser.summoner_ids), " summoners found."
		
		return parser.summoner_ids

class Command(BaseCommand):
	help = 'Update the stored challenger ladder.'
	
	def handle(self, *args, **options):
		#Benchmarking
		start = time.clock()
		
		#Store the ladder data in redis
		db = RedisConnection()
		
		for region_code, region_name in REGION_CHOICES: #For each region specified in the models file
			self.stdout.write(region_name)
			for tier in LADDER_URLS.keys(): #For each of the tiers in that region
				self.stdout.write("\t" + dict(TIER_CHOICES)[tier])
				summoner_ids = GetSummonersInTier(self.stdout, region_code, tier)
				db.set( region_code + str(tier), cPickle.dumps(summoner_ids) )
			
		print "Finished updating ladders in " + str(time.clock() - start) + " seconds."