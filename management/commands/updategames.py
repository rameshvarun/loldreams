from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from loldreams.models import *

from HTMLParser import HTMLParser


import urllib2
import urllib
import time
import shelve
import json
import datetime

API_BASE_URL = 'https://prod.api.pvp.net/api/lol'
	
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
		shelf = shelve.open("ladder.cache")
		
		for region_code, region_name in REGION_CHOICES: #For each region specified in the models file
			self.stdout.write("Getting games for " + region_code + " challenger tier.")
			
			summoner_ids = shelf[ region_code + '_challenger_ids'] #Get summoner ids from challenger tier from the shelf file
			
			for id in summoner_ids:
				for game in GetRecentGames(id, region_code):
					play_date = datetime.datetime.fromtimestamp(game['createDate']/1000.0)
					
					if game['subType'] == 'RANKED_SOLO_5x5' and len( Game.objects.filter(riotid=game['gameId']) ) == 0:
						gameObj = Game( riotid=game['gameId'],
							tier = CHALLENGER,
							date = play_date,
							region = region_code
						)
						
						#Find out if player's team won or not
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
								
						#Persist final game to database
						gameObj.save()
				
		shelf.close() #Close shelf
		self.stdout.write( str(len(Game.objects.all())) + " game entries stored in the database." ) #Take stock of how many games are stored in the database