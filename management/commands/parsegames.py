from django.core.management.base import BaseCommand, CommandError
from loldreams.models import *

def GetSummonersInTier(out, region, tier):
	summoners = []
	out.write('Getting a list of all summoner names in tier ' + tier + ' and region ' + region)
	
	out.write(str(len(summoners)) + " summoners found.")
	return summoners

class Command(BaseCommand):
	help = 'Populate the database with parsed games from the API'
	
	def handle(self, *args, **options):
		GetSummonersInTier(self.stdout, "na", "Challenger")