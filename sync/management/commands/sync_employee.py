from django.core.management.base import BaseCommand

from sync.services import run_sync


class Command(BaseCommand):
    help = "Fetch employees from the HR API and sync them into the local store."

    def handle(self, *args, **options):
        result = run_sync()
        self.stdout.write(self.style.SUCCESS(
            f"fetched={result['fetched']} created={result['created']} "
            f"updated={result['updated']} failed={result['failed']}"
        ))
        for err in result["errors"]:
            self.stdout.write(self.style.WARNING(f"  - {err}"))
