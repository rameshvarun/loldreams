from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from loldreams.models import *

from HTMLParser import HTMLParser
from django.core.cache import cache

import urllib2
import urllib
import time
import json
import cPickle



def GetChallengerTier(out, region_code):
	time.sleep(1) #Rate limit API calls

	API_BASE_URL = 'https://' + region_code + '.api.pvp.net/api/lol'
	url = API_BASE_URL + '/' + region_code + '/v2.4/league/challenger?type=RANKED_SOLO_5x5&api_key=' + settings.RIOT_API_KEY
	out.write( 'Querying ' + url )
	response = json.loads( urllib2.urlopen(url).read() )

	return [summoner['playerOrTeamId'] for summoner in response['entries']]
