# kitchen/management/commands/cleanup_deleted.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from kitchen.models import Recipe


class Command(BaseCommand):
    help = 'Hard delete books soft-deleted more than 1 day ago.'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=1)
        expired = Recipe.all_objects.filter(is_deleted=True, deleted_at__lt=cutoff)
        count = expired.count()
        for b in expired:
            b.delete(hard=True)
        self.stdout.write(self.style.SUCCESS(f'Hard-deleted {count} Recipy'))