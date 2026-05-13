# kitchen/cron.py
from django.core.management import call_command


def run_cleanup():
    call_command('cleanup_deleted')
