from django.db import models

# Champion model
class Champion(models.Model):
	name = models.CharField(max_length=200)
	riotid = models.IntegerField() #Id assigned by Riot in the API
	
	def __unicode__(self):
		return self.name

# Store game information
class Game(models.Model):
	riotid = models.IntegerField() #Id assigned by Riot in the API
	tier = models.IntegerField() #Store the tier level of the game
	
	#Champions of team 1 - this is always the team of the player that we got the data for the game from
	team1 = models.ManyToManyField(Champion, related_name='team1', blank=True)
	
	#Champions of team 2
	team2 = models.ManyToManyField(Champion, related_name='team2', blank=True)
	
	result = models.BooleanField() #True if team 1 won, false if team 2 won
	
CHALLENGER = 0
DIAMOND = 1