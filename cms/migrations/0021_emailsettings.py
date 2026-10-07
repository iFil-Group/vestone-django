from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0020_tura03"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "smtp_host",
                    models.CharField(
                        blank=True,
                        help_text="Puste — ustawienia z pliku .env na serwerze.",
                        max_length=255,
                        verbose_name="Serwer SMTP",
                    ),
                ),
                (
                    "smtp_port",
                    models.PositiveIntegerField(default=587, verbose_name="Port SMTP"),
                ),
                (
                    "smtp_username",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Użytkownik SMTP"
                    ),
                ),
                (
                    "smtp_password",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Hasło SMTP"
                    ),
                ),
                (
                    "smtp_use_tls",
                    models.BooleanField(default=True, verbose_name="Połączenie TLS"),
                ),
                (
                    "default_from_email",
                    models.EmailField(
                        blank=True,
                        help_text="From w wiadomościach wychodzących z formularzy.",
                        max_length=254,
                        verbose_name="Adres nadawcy",
                    ),
                ),
                (
                    "default_notification_email",
                    models.EmailField(
                        blank=True,
                        help_text="Gdy oferta pracy nie ma własnego adresu na CV. Formularze promocji — osobno przy każdym formularzu.",
                        max_length=254,
                        verbose_name="Domyślny odbiorca powiadomień",
                    ),
                ),
            ],
            options={
                "verbose_name": "Konfiguracja e-mail",
                "verbose_name_plural": "Konfiguracja e-mail",
            },
        ),
    ]
