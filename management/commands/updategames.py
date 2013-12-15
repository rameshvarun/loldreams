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
		summoner_ids = shelf['na_challenger_ids']
		shelf.close()
		
		for id in summoner_ids:
			for game in GetRecentGames(id, "na"):
				if game['subType'] == 'RANKED_SOLO_5x5' and len( Game.objects.filter(riotid=game['gameId']) ) == 0:
					gameObj = Game( riotid=game['gameId'],
									tier=CHALLENGER,
									date=datetime.datetime.fromtimestamp(game['createDate']/1000.0)
									)
					
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