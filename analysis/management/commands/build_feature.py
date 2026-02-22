from django.core.management.base import BaseCommand
from analysis.services.feature_builder import build_player_features  # 你自己的函数

class Command(BaseCommand):
    help = "Build player feature vectors"

    def handle(self, *args, **options):
        build_player_features()
        self.stdout.write(self.style.SUCCESS("Feature vectors built successfully"))