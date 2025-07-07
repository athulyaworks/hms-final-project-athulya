import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medinex.settings')

app = Celery('medinex')

# Use settings with CELERY_ prefix from Django settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover task modules in installed apps.
app.autodiscover_tasks()

# Optional debug task to test celery.
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Define periodic tasks using celery beat schedule.
app.conf.beat_schedule = {
    'send-appointment-reminders-every-morning': {
        'task': 'hospital.tasks.send_appointment_reminders',
        'schedule': crontab(hour=8, minute=0),  # every day 8:00 AM
    },
    'send-lab-report-notifications-every-morning': {
        'task': 'hospital.tasks.send_lab_report_notifications',
        'schedule': crontab(hour=9, minute=0),  # every day 9:00 AM
    },
    'send-bill-due-reminders-every-morning': {
        'task': 'hospital.tasks.send_bill_due_reminders',
        'schedule': crontab(hour=10, minute=0),  # every day 10:00 AM
    },
}
