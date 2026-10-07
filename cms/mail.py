from django.conf import settings
from django.core.mail import EmailMessage, get_connection


def get_cms_mail_connection():
    from cms.models import EmailSettings

    email_settings = EmailSettings.load()
    host = (email_settings.smtp_host or "").strip()
    if not host:
        return None
    return get_connection(
        backend=settings.EMAIL_BACKEND,
        host=host,
        port=email_settings.smtp_port or 587,
        username=(email_settings.smtp_username or "").strip() or None,
        password=email_settings.smtp_password or None,
        use_tls=email_settings.smtp_use_tls,
    )


def get_cms_from_email():
    from cms.models import EmailSettings

    email_settings = EmailSettings.load()
    configured = (email_settings.default_from_email or "").strip()
    return configured or settings.DEFAULT_FROM_EMAIL


def get_default_notification_recipient():
    from cms.models import EmailSettings, SiteSettings

    email_settings = EmailSettings.load()
    configured = (email_settings.default_notification_email or "").strip()
    if configured:
        return configured
    site_email = (SiteSettings.load().email or "").strip()
    if site_email:
        return site_email
    return settings.DEFAULT_FROM_EMAIL


def send_cms_mail(subject, message, recipient_list):
    connection = get_cms_mail_connection()
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=get_cms_from_email(),
        to=recipient_list,
        connection=connection,
    )
    email.send(fail_silently=False)
    return email
