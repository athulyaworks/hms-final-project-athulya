from django.core.mail import send_mail
from django.conf import settings

def send_notification_email(subject, message, recipient):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  #from
        [recipient],  # to
        fail_silently=False,
    )


def is_receptionist(user):
    return user.is_authenticated and user.role == 'receptionist'
