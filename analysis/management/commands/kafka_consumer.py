from django.core.management.base import BaseCommand
from analysis.kafka.consumer import consumer

class Command(BaseCommand):
    help = "Run Kafka consumer"

    def handle(self, *args, **options):
        run_consumer()