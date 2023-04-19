# Generated by Django 4.1.7 on 2023-04-19 04:14

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("kaax_app", "0007_entrenamientos"),
    ]

    operations = [
        migrations.CreateModel(
            name="Verificaciones",
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
                ("ip_address", models.CharField(max_length=255)),
                ("email_address", models.EmailField(max_length=254)),
                ("billing_state", models.CharField(max_length=255)),
                ("user_agent", models.CharField(max_length=255)),
                ("billing_postal", models.CharField(max_length=255)),
                ("phone_number", models.CharField(max_length=20)),
                ("EVENT_TIMESTAMP", models.CharField(max_length=255)),
                ("billing_address", models.CharField(max_length=255)),
                ("resultado", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "empresa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="kaax_app.empresa",
                    ),
                ),
            ],
            options={
                "db_table": "verificaciones",
            },
        ),
    ]