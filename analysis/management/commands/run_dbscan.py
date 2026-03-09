from django.core.management.base import BaseCommand
from analysis.services.do_dbscan import run_dimension_cluster


class Command(BaseCommand):

    help = "Run dimension clustering"

    def handle(self, *args, **options):
        run_dimension_cluster()
        self.stdout.write(self.style.SUCCESS("Dimension clustering done"))