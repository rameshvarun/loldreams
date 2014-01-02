from django.shortcuts import render
from django.http import HttpResponse

from loldreams.models import *

import json
import time

from django.views.decorators.cache import cache_page

def jsonResponse(jsonDict):
	return HttpResponse(json.dumps(jsonDict, indent=4), content_type="application/json")

@cache_page(60) #Cache page on timeout of one minute
def home(request):
	context = {
		"champions" : Champion.objects.all(),
		"numgames" : len(Game.objects.all())
	}
	
	return render(request, 'home.html', context)
	
def win_rate(request):
	#Benchmarking
	start = time.clock()
	
	#Need to have two queries, as the specific champion combination might match either team1 or team2
	team1_games = Game.objects.filter(region = request.GET['region'] )
	team2_games = Game.objects.filter(region = request.GET['region'] )
	
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
		
	return jsonResponse(response)
	
SMALLEST_SAMPLE_SIZE = 5
	
def reccomendations(request):
	#Benchmarking
	start = time.clock()
	
	#Need to have two queries, as the specific champion combination might match either team1 or team2
	team1_games = Game.objects.filter(region = request.GET['region'] )
	team2_games = Game.objects.filter(region = request.GET['region'] )
	
	#Filter down by champion id
	for champion_id in request.GET.getlist('id'):
		team1_games = team1_games.filter(team1__riotid = champion_id )
		team2_games = team2_games.filter(team2__riotid = champion_id )
		
	if len(team1_games) + len(team2_games) < SMALLEST_SAMPLE_SIZE:
		return jsonResponse({ 'error' : 'This champion does not have a large enough sample size.'})
	
	response = {
		'champions' : []
	}
	
	for champion in Champion.objects.all():
		if str(champion.riotid) not in request.GET.getlist('id'):
			result = {}
			possible_team1 = team1_games.filter(team1 = champion)
			possible_team2 = team2_games.filter(team2 = champion)
			
			sample_size = len(possible_team1) + len(possible_team2)
			
			if sample_size >= SMALLEST_SAMPLE_SIZE:
				possible_team1 = possible_team1.filter(result=True)
				possible_team2 = possible_team2.filter(result=False)
				
				wins = len(possible_team1) + len(possible_team2)
				
				result['name'] = champion.name
				result['id'] = champion.riotid
				result['winrate'] = float(wins)/sample_size
				result['sample_size'] = sample_size
				
				response['champions'].append(result)
	
	response['time'] = time.clock() - start
	return jsonResponse(response)