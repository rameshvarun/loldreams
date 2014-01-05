from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
from loldreams.models import *

import json
import time

from django.views.decorators.cache import cache_page

def jsonResponse(jsonDict):
	return HttpResponse(json.dumps(jsonDict, indent=4), content_type="application/json")

@cache_page(60 * 60 * 24) #Cache page on timeout of one whole day
def home(request):
	context = {
		"champions" : Champion.objects.all(),
		"numgames" : len(Game.objects.all()),
		"comments_enabled" : True
	}
	
	return render(request, 'home.html', context)
	
CACHE_RESULT_TIME = 60 * 60 * 24 #Cache win-rate and recommendations for one whole day
def win_rate(request):
	#Benchmarking
	start = time.clock()
	
	#Create a hash, to be used eventually for caching results
	hash = 'w' + request.GET['region'] + ','.join(sorted(request.GET.getlist('tier'))) + ','.join(sorted(request.GET.getlist('id')))
	
	#Check if the result is already in the cache
	if hash in cache:
		return HttpResponse( cache.get(hash), content_type="application/json")
		
	#Need to have two queries, as the specific champion combination might match either team1 or team2
	team1_games = Game.objects.filter(region = request.GET['region'] )
	team2_games = Game.objects.filter(region = request.GET['region'] )
	
	#Filter down by tier
	team1_games = team1_games.filter(tier__in = request.GET.getlist('tier'))
	team2_games = team2_games.filter(tier__in = request.GET.getlist('tier'))
	
	#Filter down by champion id
	for champion_id in request.GET.getlist('id'):
		team1_games = team1_games.filter(team1__riotid = champion_id )
		team2_games = team2_games.filter(team2__riotid = champion_id )
		
	sample_size = len(team1_games) + len(team2_games)
	
	team1_games = team1_games.filter(result=True) #Games won by team 1
	team2_games = team2_games.filter(result=False) #Games won by team 2
	wins = len(team1_games) + len(team2_games)
	losses = sample_size - wins
	
	response = {
		'sample_size' : sample_size,
		'wins' : wins,
		'losses' : losses,
		'time' : time.clock() - start
		}
	
	#If we can, calculate a win rate
	if sample_size > 0:
		response['winrate'] = (float(wins)/(wins + losses))
	
	#Put result in cache, then return
	json_string = json.dumps(response, indent=4)
	cache.set(hash, json_string, CACHE_RESULT_TIME)
	return HttpResponse( json_string, content_type="application/json")
	
SMALLEST_SAMPLE_SIZE = 10
	
def reccomendations(request):
	#Benchmarking
	start = time.clock()
	
	#Create a hash, to be used eventually for caching results
	hash = 'r' + request.GET['region'] + ','.join(sorted(request.GET.getlist('tier'))) + ','.join(sorted(request.GET.getlist('id')))
	
	#Check if the result is already in the cache
	if hash in cache:
		return HttpResponse( cache.get(hash), content_type="application/json")
		
	#Need to have two queries, as the specific champion combination might match either team1 or team2
	team1_games = Game.objects.filter(region = request.GET['region'] )
	team2_games = Game.objects.filter(region = request.GET['region'] )
	
	#Filter down by tier
	team1_games = team1_games.filter(tier__in = request.GET.getlist('tier'))
	team2_games = team2_games.filter(tier__in = request.GET.getlist('tier'))
	
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
	
	#Put result in cache, then return
	json_string = json.dumps(response, indent=4)
	cache.set(hash, json_string, CACHE_RESULT_TIME)
	return HttpResponse( json_string, content_type="application/json")