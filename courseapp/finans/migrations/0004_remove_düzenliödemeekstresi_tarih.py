# Generated by Django 5.1.6 on 2025-02-25 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finans', '0003_düzenliödemeekstresi_tarih'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='düzenliödemeekstresi',
            name='tarih',
        ),
    ]
