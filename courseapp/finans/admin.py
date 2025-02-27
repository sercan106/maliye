# finans/admin.py
from django.contrib import admin
from .models import (
    GelirKategori, GiderKategori, Gelir, Gider, KrediKarti, 
    KrediKartiEkstre, KrediKartiÖdeme, DüzenliÖdeme, DüzenliÖdemeEkstresi
)

# Gelir Kategori Admin
@admin.register(GelirKategori)
class GelirKategoriAdmin(admin.ModelAdmin):
    list_display = ('isim', 'üst_kategori')
    list_filter = ('üst_kategori',)
    search_fields = ('isim',)

# Gider Kategori Admin
@admin.register(GiderKategori)
class GiderKategoriAdmin(admin.ModelAdmin):
    list_display = ('isim', 'üst_kategori')
    list_filter = ('üst_kategori',)
    search_fields = ('isim',)

# Gelir Admin
@admin.register(Gelir)
class GelirAdmin(admin.ModelAdmin):
    list_display = ('kullanıcı', 'kategori', 'miktar', 'para_birimi', 'tarih')
    list_filter = ('kullanıcı', 'kategori', 'para_birimi', 'tarih')
    search_fields = ('kullanıcı__username', 'açıklama')

# Gider Admin
@admin.register(Gider)
class GiderAdmin(admin.ModelAdmin):
    list_display = ('kullanıcı', 'kategori', 'miktar', 'para_birimi', 'tarih')
    list_filter = ('kullanıcı', 'kategori', 'para_birimi', 'tarih')
    search_fields = ('kullanıcı__username', 'açıklama')

# Kredi Kartı Admin
@admin.register(KrediKarti)
class KrediKartiAdmin(admin.ModelAdmin):
    list_display = ('kullanıcı', 'isim', 'toplam_borc', 'limit', 'son_ödeme_günü')
    list_filter = ('kullanıcı',)
    search_fields = ('kullanıcı__username', 'isim')

# Kredi Kartı Ekstre Admin
@admin.register(KrediKartiEkstre)
class KrediKartiEkstreAdmin(admin.ModelAdmin):
    list_display = ('kredi_karti', 'son_ödeme_tarihi', 'asgari_tutar', 'ödendi_mi')
    list_filter = ('kredi_karti', 'ödendi_mi', 'ay', 'yıl')
    search_fields = ('kredi_karti__isim',)

# Kredi Kartı Ödeme Admin
@admin.register(KrediKartiÖdeme)
class KrediKartiÖdemeAdmin(admin.ModelAdmin):
    list_display = ('ödeme_durumu', 'miktar', 'faiz', 'tarih', 'para_birimi')
    list_filter = ('para_birimi', 'tarih')
    search_fields = ('ödeme_durumu__kredi_karti__isim',)

# Düzenli Ödeme Admin
@admin.register(DüzenliÖdeme)
class DüzenliÖdemeAdmin(admin.ModelAdmin):
    list_display = ('kullanıcı', 'açıklama', 'miktar', 'para_birimi', 'ödeme_günü', 'kategori')
    list_filter = ('kullanıcı', 'para_birimi', 'kategori')
    search_fields = ('kullanıcı__username', 'açıklama')

# Düzenli Ödeme Ekstresi Admin
@admin.register(DüzenliÖdemeEkstresi)
class DüzenliÖdemeEkstresiAdmin(admin.ModelAdmin):
    list_display = ('düzenli_ödeme', 'son_ödeme_tarihi', 'ödendi_mi')
    list_filter = ('ödendi_mi', 'ay', 'yıl')
    search_fields = ('düzenli_ödeme__açıklama',)