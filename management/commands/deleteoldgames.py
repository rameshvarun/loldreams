from django.core.management.base import BaseCommand, CommandError
from loldreams.models import *

from datetime import *

DAYS = 30

class Command(BaseCommand):
	help = 'Populate the database with parsed games from the API'
	
	def handle(self, *args, **options):
		date_limit = datetime.now() - timedelta(days=DAYS)
		games = Game.objects.filter(date__lte=date_limit)
		self.stdout.write( str(len(games)) + " games over " + str(DAYS) + " days old deleted from database.")
		games.delete()