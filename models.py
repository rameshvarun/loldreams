from django.db import models
from django.conf import settings

import datetime
import json
import urllib2

na_json = None
def get_na_json():
	global na_json
	if na_json == None:
		url = "http://ddragon.leagueoflegends.com/realms/na.json"
		na_json = json.loads( urllib2.urlopen(url).read() )
	return na_json

champion_json = None
def get_champion_json():
	global champion_json
	if champion_json == None:
		url = "http://ddragon.leagueoflegends.com/cdn/" + get_na_json()['n']['champion'] + "/data/en_US/champion.json"
		champion_json = json.loads( urllib2.urlopen(url).read() )
	return champion_json

# Champion model
class Champion(models.Model):
	name = models.CharField(max_length=200) # The full actual name of the character (language dependant)
	key = models.CharField(max_length=200) # Text identifier for the champion (language dependant)
	riotid = models.IntegerField(primary_key=True) #Id assigned by Riot in the API

	#Comma separated, lowercase list of the roles that the champion can play
	#First role in list should be the primary role
	roles = models.CharField(max_length=200, blank=True)

	def __unicode__(self):
		return self.name

	def info(self):
		return get_champion_json()['data'][self.name]

#For creating arbitrary pages (like the about page)
class Page(models.Model):
	url = models.CharField( max_length=300, blank=True )
	html = models.TextField(blank=True)

	def __unicode__(self):
		return self.url

#Region choices
REGION_CHOICES = (
    ('na', 'North America'),
    ('euw', 'Europe West'),
    ('eune', 'Europe Nordic & East')
)

#Tiers
CHALLENGER = 0
DIAMONDI = 1
TIER_CHOICES = (
	(CHALLENGER, "Challenger"),
	(DIAMONDI, "Diamond I")
)

# Store game information
class Game(models.Model):
	riotid = models.IntegerField(primary_key=True) #Id assigned by Riot in the API
	tier = models.IntegerField() #Store the tier level of the game

	#Champions of team 1 - this is always the team of the player that we got the data for the game from
	team1 = models.ManyToManyField(Champion, related_name='team1', blank=True, db_index=True)

	#Champions of team 2
	team2 = models.ManyToManyField(Champion, related_name='team2', blank=True, db_index=True)

	result = models.BooleanField() #True if team 1 won, false if team 2 won

	date = models.DateTimeField('Date played') #The date the game was played

	region = models.CharField(max_length=5, blank=True, choices=REGION_CHOICES) #The region in which the game was played
