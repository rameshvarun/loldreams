from django.shortcuts import render
from django.http import HttpResponse

from loldreams.models import *

import json
import time

def home(request):
	context = {}
	return render(request, 'main.html', context)
	
def win_rate(request):
	#Benchmarking
	start = time.clock()
	
	#Need to have two queries, as the specific champion combination might match either team1 or team2
	team1_games = Game.objects.all()
	team2_games = Game.objects.all()
	
	#Filter down by champion id
	for champion_id in request.GET.getlist('id'):
		team1_games = team1_games.filter(team1__riotid = champion_id )
		team2_games = team2_games.filter(team2__riotid = champion_id )
		
	sample_size = len(team1_games) + len(team2_games)
		
	wins = 0
	losses = 0
	for game in team1_games:
		if game.result:
			wins += 1
		else:
			losses += 1
			
	for game in team2_games:
		if not game.result:
			wins += 1
		else:
			losses += 1
	
	response = {
		'sample_size' : sample_size,
		'wins' : wins,
		'losses' : losses,
		'time' : time.clock() - start
		}
	
	#If we can, calculate a win rate
	if sample_size > 0:
		response['winrate'] = (float(wins)/(wins + losses))
		
	return HttpResponse(json.dumps(response, indent=4), content_type="application/json")