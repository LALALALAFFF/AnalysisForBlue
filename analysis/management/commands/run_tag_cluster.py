from django.core.management.base import BaseCommand
from analysis.tag_cluster_service import run_tag_clustering


class Command(BaseCommand):

    help = "Run player tag clustering"

    def handle(self, *args, **options):
        run_tag_clustering()
        self.stdout.write(self.style.SUCCESS("Tag clustering done"))