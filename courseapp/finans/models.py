from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import calendar
from decimal import Decimal  # Decimal türünü içe aktar

# Sabitler
PARA_BIRIMI_SECENEKLERI = [
    ('TL', 'Türk Lirası'),
    ('USD', 'Amerikan Doları'),
    ('GOLD', 'Altın'),
    ('RUB', 'Rus Rublesi'),
]

# Gelir Kategori Modeli
class GelirKategori(models.Model):
    isim = models.CharField(max_length=100)
    üst_kategori = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.isim

# Gider Kategori Modeli
class GiderKategori(models.Model):
    isim = models.CharField(max_length=100)
    üst_kategori = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.isim

# Gelir Modeli
class Gelir(models.Model):
    kullanıcı = models.ForeignKey(User, on_delete=models.CASCADE)
    kategori = models.ForeignKey(GelirKategori, on_delete=models.SET_NULL, null=True, blank=True)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    para_birimi = models.CharField(max_length=4, choices=PARA_BIRIMI_SECENEKLERI)
    açıklama = models.TextField(blank=True)
    tarih = models.DateField()

    def __str__(self):
        return f"{self.kullanıcı.username} - {self.miktar} {self.para_birimi}"

# Gider Modeli
class Gider(models.Model):
    kullanıcı = models.ForeignKey(User, on_delete=models.CASCADE)
    kategori = models.ForeignKey(GiderKategori, on_delete=models.SET_NULL, null=True, blank=True)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    para_birimi = models.CharField(max_length=4, choices=PARA_BIRIMI_SECENEKLERI)
    açıklama = models.TextField(blank=True)
    tarih = models.DateField()

    def __str__(self):
        return f"{self.kullanıcı.username} - {self.miktar} {self.para_birimi}"

# Kredi Kartı Modeli
class KrediKarti(models.Model):
    kullanıcı = models.ForeignKey(User, on_delete=models.CASCADE)
    isim = models.CharField(max_length=100)
    toplam_borc = models.DecimalField(max_digits=10, decimal_places=2)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    son_ödeme_günü = models.IntegerField()
    asgari_ödeme_yüzdesi = models.DecimalField(max_digits=5, decimal_places=2)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.ilk_ödeme_durumu_oluştur()

    def ilk_ödeme_durumu_oluştur(self):
        şuanki_tarih = timezone.now()
        ay_sonu = calendar.monthrange(şuanki_tarih.year, şuanki_tarih.month)[1]
        son_ödeme_günü = min(self.son_ödeme_günü, ay_sonu)
        son_ödeme_tarihi = şuanki_tarih.replace(day=son_ödeme_günü)

        ekstre = KrediKartiEkstre(
            kredi_karti=self,
            son_ödeme_tarihi=son_ödeme_tarihi,
            asgari_tutar=self.toplam_borc * (self.asgari_ödeme_yüzdesi / 100),
            ödendi_mi=False,
            ay=şuanki_tarih.month,
            yıl=şuanki_tarih.year,
        )
        ekstre.save()

    def __str__(self):
        return f"{self.kullanıcı.username}'ın {self.isim} Kartı"

# Kredi Kartı Ekstre Modeli
class KrediKartiEkstre(models.Model):
    kredi_karti = models.ForeignKey(KrediKarti, on_delete=models.CASCADE)
    son_ödeme_tarihi = models.DateField(default=timezone.now)
    ay = models.IntegerField(editable=False, blank=True, null=True)
    yıl = models.IntegerField(editable=False, blank=True, null=True)
    asgari_tutar = models.DecimalField(max_digits=10, decimal_places=2)
    ödendi_mi = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.ay = self.son_ödeme_tarihi.month
        self.yıl = self.son_ödeme_tarihi.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kredi_karti.isim} - {self.son_ödeme_tarihi.strftime('%B %Y')}"

# Kredi Kartı Ödeme Modeli
class KrediKartiÖdeme(models.Model):
    ödeme_durumu = models.OneToOneField(KrediKartiEkstre, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    faiz = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tarih = models.DateField(default=timezone.now)
    para_birimi = models.CharField(max_length=4, choices=PARA_BIRIMI_SECENEKLERI, default='TL')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ödeme_durumu.ödendi_mi = True
        self.ödeme_durumu.save()
        kredi_karti = self.ödeme_durumu.kredi_karti
        kredi_karti.toplam_borc = kredi_karti.toplam_borc - (self.miktar - self.faiz)
        KrediKarti.objects.filter(pk=kredi_karti.pk).update(toplam_borc=kredi_karti.toplam_borc)

        # Gider kategorisi oluştur
        kategori, _ = GiderKategori.objects.get_or_create(isim="Kredi Kartı Ödemesi")

        Gider.objects.create(
            kullanıcı=kredi_karti.kullanıcı,
            kategori=kategori,
            miktar=self.miktar,
            para_birimi=self.para_birimi,
            açıklama=f"{kredi_karti.isim} - Kredi Kartı Ödemesi (Faiz: {self.faiz})",
            tarih=timezone.now().date()
        )

    def __str__(self):
        return f"{self.ödeme_durumu.kredi_karti.isim} - {self.miktar}"

# Düzenli Ödeme Modeli
class DüzenliÖdeme(models.Model):
    kullanıcı = models.ForeignKey(User, on_delete=models.CASCADE)
    açıklama = models.CharField(max_length=100)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    para_birimi = models.CharField(max_length=4, choices=PARA_BIRIMI_SECENEKLERI)
    ödeme_günü = models.IntegerField()
    kategori = models.ForeignKey(GiderKategori, on_delete=models.SET_NULL, null=True, blank=True)  # Üst/alt kategori seçimi

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.ilk_ödeme_durumu_oluştur()

    def ilk_ödeme_durumu_oluştur(self):
        şuanki_tarih = timezone.now()
        ay_sonu = calendar.monthrange(şuanki_tarih.year, şuanki_tarih.month)[1]
        ödeme_günü = min(self.ödeme_günü, ay_sonu)
        son_ödeme_tarihi = şuanki_tarih.replace(day=ödeme_günü)

        ekstre = DüzenliÖdemeEkstresi(
            düzenli_ödeme=self,
            son_ödeme_tarihi=son_ödeme_tarihi,
            ödendi_mi=False,
            ay=şuanki_tarih.month,
            yıl=şuanki_tarih.year,
        )
        ekstre.save()

    def __str__(self):
        return f"{self.açıklama} - {self.miktar} {self.para_birimi}"

# Düzenli Ödeme Ekstresi Modeli
class DüzenliÖdemeEkstresi(models.Model):
    düzenli_ödeme = models.ForeignKey(DüzenliÖdeme, on_delete=models.CASCADE)
    son_ödeme_tarihi = models.DateField()
    ödendi_mi = models.BooleanField(default=False)
    ay = models.IntegerField(editable=False, blank=True, null=True)
    yıl = models.IntegerField(editable=False, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.ay = self.son_ödeme_tarihi.month
        self.yıl = self.son_ödeme_tarihi.year
        super().save(*args, **kwargs)

        # Eğer ödendi_mi True ise Gider ekle
        if self.ödendi_mi:
            # DüzenliÖdeme'deki kategori kullanılacak (üst/alt kategori dahil)
            kategori = self.düzenli_ödeme.kategori

            Gider.objects.create(
                kullanıcı=self.düzenli_ödeme.kullanıcı,
                kategori=kategori,  # Üst ve alt kategori bilgisiyle birlikte
                miktar=self.düzenli_ödeme.miktar,
                para_birimi=self.düzenli_ödeme.para_birimi,
                açıklama=f"{self.düzenli_ödeme.açıklama} - Düzenli Ödeme",
                tarih=timezone.now().date()  # Şimdiki tarih otomatik olarak ekleniyor
            )

    def __str__(self):
        return f"{self.düzenli_ödeme.açıklama} - {self.son_ödeme_tarihi}"