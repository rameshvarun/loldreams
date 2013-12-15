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
	
def GetRecentGames(id, region):
	time.sleep(1)
	url = API_BASE_URL + '/' + region + '/v1.1/game/by-summoner/' + str(id) + '/recent?api_key=' + settings.RIOT_API_KEY
	print url
	return json.loads( urllib2.urlopen(url).read() )['games']
	
def GetChampionById(id):
	return Champion.objects.get(riotid=id)

class Command(BaseCommand):
	help = 'Populate the database with parsed games from the API'
	
	def handle(self, *args, **options):
		shelf = shelve.open("laddercache")
		
		summoner_names = []
		if shelf.has_key('names'):
			summoner_names = shelf['names']
		else:
			summoner_names = GetSummonersInTier(self.stdout, "na", "Challenger")
			shelf['names'] = summoner_names
			shelf.sync()
			
		summoner_ids = []
		if shelf.has_key('ids'):
			summoner_ids = shelf['ids']
		else:
			summoner_ids = [ GetSummonerProfileByName(name, 'na')['id'] for name in summoner_names]
			shelf['ids'] = summoner_ids 
			shelf.sync()
		
		for id in summoner_ids:
			for game in GetRecentGames(id, "na"):
				if game['subType'] == 'RANKED_SOLO_5x5' and len( Game.objects.filter(riotid=game['gameId']) ) == 0:
					gameObj = Game( riotid=game['gameId'], tier=CHALLENGER )
					
					#Find out if player's team won
					for statistic in game['statistics']:
						if statistic['name'] == "LOSE":
							gameObj.result = False
							break
						if statistic['name'] == "WIN":
							gameObj.result = True
							break
					
					#Save to database before figuring out teams
					gameObj.save()
					
					#Add player to team1
					gameObj.team1.add( GetChampionById(game['championId']) )
					
					#Add other players to teams
					for player in game['fellowPlayers']:
						champion = GetChampionById(player['championId'])
						if player['teamId'] == game['teamId']:
							gameObj.team1.add( champion )
						else:
							gameObj.team2.add( champion )
					
					#Persist to database
					gameObj.save()
				
		shelf.close()