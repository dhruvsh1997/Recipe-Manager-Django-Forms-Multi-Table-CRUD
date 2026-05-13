# kitchen/cron.py
from django.core.management import call_command


def run_cleanup():
    """
    Entry point for django-crontab.
    Delegates to the existing `cleanup_deleted` management command so the
    same logic is runnable both manually (python manage.py cleanup_deleted)
    and on a schedule.
    """
    call_command('cleanup_deleted')
