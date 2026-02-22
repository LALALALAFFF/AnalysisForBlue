from django.core.management.base import BaseCommand
from django.utils import timezone
from player.models import PlayerBasic
from player.models import ActionLog


class Command(BaseCommand):
    help = "Backfill PlayerBasic from ActionLog"

    def handle(self, *args, **options):
        uids = (
            ActionLog.objects
            .values_list("uid", flat=True)
            .distinct()
        )

        created_count = 0

        for uid in uids:
            player, created = PlayerBasic.objects.get_or_create(
                uid=uid,
                defaults={
                    "username": f"user_{uid}",
                    "register_time": timezone.now(),
                    "last_login": timezone.now(),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created PlayerBasic uid={uid}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count} PlayerBasic records."
            )
        )
