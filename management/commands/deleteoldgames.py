from django.core.management.base import BaseCommand, CommandError
from loldreams.models import *
from datetime import *

DAYS = 28

class Command(BaseCommand):
	help = 'Deletes games older than a certain amount of days.'
	
	def handle(self, *args, **options):
		date_limit = datetime.now() - timedelta(days=DAYS)
		games = Game.objects.filter(date__lte=date_limit)
		self.stdout.write( str(len(games)) + " games over " + str(DAYS) + " days old deleted from database.")
		games.delete()