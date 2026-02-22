# analysis/management/commands/build_features.py

from django.core.management.base import BaseCommand
from analysis.services.feature_builder import build_player_features
from player.models import PlayerBasic


class Command(BaseCommand):
    help = "Build player feature vectors from ActionLog"

    def add_arguments(self, parser):
        parser.add_argument(
            "--uid",
            type=int,
            help="Build features for a specific player uid"
        )

    def handle(self, *args, **options):
        uid = options.get("uid")

        if uid:
            self.stdout.write(f"Building features for uid={uid}")
            build_player_features(uid)
        else:
            self.stdout.write("Building features for ALL players")
            for player in PlayerBasic.objects.all():
                build_player_features(player.uid)

        self.stdout.write(self.style.SUCCESS("Feature building completed"))
