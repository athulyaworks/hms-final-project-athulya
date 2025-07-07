from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils.timezone import now
import json

class Command(BaseCommand):
    help = 'Set up periodic Celery tasks for reminders and billing'

    def handle(self, *args, **kwargs):
        try:
            # Appointment reminder every hour
            appointment_cron, _ = CrontabSchedule.objects.get_or_create(
                minute='0', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
            )
            PeriodicTask.objects.get_or_create(
                crontab=appointment_cron,
                name='Hourly Appointment Reminders',
                task='hospital.tasks.send_upcoming_appointment_reminders',
                defaults={'start_time': now(), 'kwargs': json.dumps({})}
            )

            # Hourly Lab Report Notification
            lab_cron, _ = CrontabSchedule.objects.get_or_create(
                minute='0', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
            )
            PeriodicTask.objects.get_or_create(
                crontab=lab_cron,
                name='Hourly Lab Report Notifications',
                task='hospital.tasks.send_lab_report_notifications',
                defaults={'start_time': now(), 'kwargs': json.dumps({})}
            )

            # Bill Due Reminder at 7 AM and 7 PM daily
            for hour in ['7', '19']:
                bill_cron, _ = CrontabSchedule.objects.get_or_create(
                    minute='0', hour=hour, day_of_week='*', day_of_month='*', month_of_year='*'
                )
                PeriodicTask.objects.get_or_create(
                    crontab=bill_cron,
                    name=f'Bill Due Reminder {hour}',
                    task='hospital.tasks.send_bill_due_reminders',
                    defaults={'start_time': now(), 'kwargs': json.dumps({})}
                )

            self.stdout.write(self.style.SUCCESS("✔ Periodic tasks set up successfully."))

        except Exception as e:
            self.stderr.write(f"[Celery Scheduler Setup Error] {e}")
