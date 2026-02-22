from django.core.management.base import BaseCommand
from analysis.clustering import run_dbscan_clustering


class Command(BaseCommand):
    help = "Run DBSCAN clustering for players"

    def add_arguments(self, parser):
        parser.add_argument("--eps", type=float, default=1.0)
        parser.add_argument("--min_samples", type=int, default=3)

    def handle(self, *args, **options):
        eps = options["eps"]
        min_samples = options["min_samples"]

        self.stdout.write(
            f"Running DBSCAN (eps={eps}, min_samples={min_samples})"
        )

        run_dbscan_clustering(
            eps=eps,
            min_samples=min_samples
        )

        self.stdout.write(self.style.SUCCESS("DBSCAN clustering finished"))
