from django.core.management.base import BaseCommand
from analysis.tag_assigner import run_assign_tags

class Command(BaseCommand):
    help = "根据特征向量为玩家打标签"

    def handle(self, *args, **kwargs):
        run_assign_tags()
        self.stdout.write(self.style.SUCCESS("All players tagged successfully"))