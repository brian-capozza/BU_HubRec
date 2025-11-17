from django.core.management.base import BaseCommand

def process_professors():
    pass

class Command(BaseCommand):
    help = "Populates the database with scraped professors"

    def handle(self, *args, **options):
        process_professors