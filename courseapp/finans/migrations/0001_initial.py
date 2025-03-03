# Generated by Django 5.1.6 on 2025-02-23 12:18

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DüzenliÖdeme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('açıklama', models.CharField(max_length=100)),
                ('miktar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('para_birimi', models.CharField(choices=[('TL', 'Türk Lirası'), ('USD', 'Amerikan Doları'), ('GOLD', 'Altın'), ('RUB', 'Rus Rublesi')], max_length=4)),
                ('ödeme_günü', models.IntegerField()),
                ('kullanıcı', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DüzenliÖdemeEkstresi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('son_ödeme_tarihi', models.DateField()),
                ('ödendi_mi', models.BooleanField(default=False)),
                ('ay', models.IntegerField(blank=True, editable=False, null=True)),
                ('yıl', models.IntegerField(blank=True, editable=False, null=True)),
                ('düzenli_ödeme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finans.düzenliödeme')),
            ],
        ),
        migrations.CreateModel(
            name='Kategori',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isim', models.CharField(max_length=100)),
                ('üst_kategori', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='finans.kategori')),
            ],
        ),
        migrations.CreateModel(
            name='Gider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('para_birimi', models.CharField(choices=[('TL', 'Türk Lirası'), ('USD', 'Amerikan Doları'), ('GOLD', 'Altın'), ('RUB', 'Rus Rublesi')], max_length=4)),
                ('açıklama', models.TextField(blank=True)),
                ('tarih', models.DateField()),
                ('kullanıcı', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('kategori', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finans.kategori')),
            ],
        ),
        migrations.CreateModel(
            name='Gelir',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('para_birimi', models.CharField(choices=[('TL', 'Türk Lirası'), ('USD', 'Amerikan Doları'), ('GOLD', 'Altın'), ('RUB', 'Rus Rublesi')], max_length=4)),
                ('açıklama', models.TextField(blank=True)),
                ('tarih', models.DateField()),
                ('kullanıcı', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('kategori', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finans.kategori')),
            ],
        ),
        migrations.CreateModel(
            name='KrediKarti',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isim', models.CharField(max_length=100)),
                ('toplam_borc', models.DecimalField(decimal_places=2, max_digits=10)),
                ('limit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('son_ödeme_günü', models.IntegerField()),
                ('asgari_ödeme_yüzdesi', models.DecimalField(decimal_places=2, max_digits=5)),
                ('kullanıcı', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='KrediKartiEkstre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('son_ödeme_tarihi', models.DateField(default=django.utils.timezone.now)),
                ('ay', models.IntegerField(blank=True, editable=False, null=True)),
                ('yıl', models.IntegerField(blank=True, editable=False, null=True)),
                ('asgari_tutar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ödendi_mi', models.BooleanField(default=False)),
                ('kredi_karti', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finans.kredikarti')),
            ],
        ),
        migrations.CreateModel(
            name='KrediKartiÖdeme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('faiz', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tarih', models.DateField(default=django.utils.timezone.now)),
                ('para_birimi', models.CharField(choices=[('TL', 'Türk Lirası'), ('USD', 'Amerikan Doları'), ('GOLD', 'Altın'), ('RUB', 'Rus Rublesi')], default='TL', max_length=4)),
                ('ödeme_durumu', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='finans.kredikartiekstre')),
            ],
        ),
    ]
