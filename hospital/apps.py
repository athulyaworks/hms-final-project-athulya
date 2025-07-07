from django.apps import AppConfig

class HospitalConfig(AppConfig):
    name = 'hospital'

    def ready(self):
        import hospital.signals  # keep existing signal logic

        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        from django.utils.timezone import now
        import json

        try:
            # Task 1: Appointment reminder every hour
            appointment_cron, _ = CrontabSchedule.objects.get_or_create(
                minute='0', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
            )
            PeriodicTask.objects.get_or_create(
                crontab=appointment_cron,
                name='Hourly Appointment Reminders',
                task='hospital.tasks.send_upcoming_appointment_reminders',
                defaults={'start_time': now(), 'kwargs': json.dumps({})}
            )

            # Task 2: Hourly Lab Report Notification
            lab_cron, _ = CrontabSchedule.objects.get_or_create(
                minute='0', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
            )
            PeriodicTask.objects.get_or_create(
                crontab=lab_cron,
                name='Hourly Lab Report Notifications',
                task='hospital.tasks.send_lab_report_notifications',
                defaults={'start_time': now(), 'kwargs': json.dumps({})}
            )

            # Task 3: Bill Due Reminder every day at 7:00 AM and 7:00 PM
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

        except Exception as e:
            print(f"[Celery Scheduler Setup Error] {e}")
