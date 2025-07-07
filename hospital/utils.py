from django.core.mail import send_mail

def send_notification_email(subject, message, recipient):
    send_mail(
        subject,
        message,
        'admin@medinex.com',  #from
        [recipient],  # to
        fail_silently=False,
    )