from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

#Gets a list of all champions, puts them into the database
class Command(BaseCommand):
	help = 'Clears the entire cache.'
	
	def handle(self, *args, **options):
		cache.clear()
		self.stdout.write('Cache successfully cleared...')