# Generated by Django 4.1.7 on 2023-04-07 01:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("kaax_app", "0002_rename_plan_id_empresa_plan_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Transaccion",
            new_name="Transacciones_Prueba",
        ),
        migrations.AlterModelTable(
            name="transacciones_prueba",
            table="transacciones_prueba",
        ),
    ]