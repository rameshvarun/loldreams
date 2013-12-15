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
	
	team1 = models.ManyToManyField(Champion, related_name='team1') #Champions of team 1
	team2 = models.ManyToManyField(Champion, related_name='team2') #Champions of team 2
	
	result = models.BooleanField() #True if team 1 won, false if team 2 won
