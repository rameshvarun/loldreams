from django.core.management.base import BaseCommand, CommandError
from loldreams.models import *

class Command(BaseCommand):
	help = 'Deletes all games in the database.'
	
	def handle(self, *args, **options):
		games = Game.objects.all()
		self.stdout.write( str(len(games)) + " games in database deleted.")
		games.delete()