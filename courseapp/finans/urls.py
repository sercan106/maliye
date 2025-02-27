# finans/urls.py
from django.urls import path
from . import views

app_name = 'finans'

urlpatterns = [

    path('', views.anasayfa, name='anasayfa'),
    path('gelir-ekle/', views.gelir_ekle, name='gelir_ekle'),
    path('gider-ekle/', views.gider_ekle, name='gider_ekle'),
    path('gelir-listesi/', views.gelir_listesi, name='gelir_listesi'),  # Yeni rota
    path('gider-listesi/', views.gider_listesi, name='gider_listesi'),  # Yeni rota
    path('kredi-karti-ekle/', views.kredi_karti_ekle, name='kredi_karti_ekle'),
    path('duzenli-odeme-ekle/', views.duzenli_ödeme_ekle, name='duzenli_ödeme_ekle'),
    path('kredi-karti-listesi/', views.kredi_karti_listesi, name='kredi_karti_listesi'),
    path('kredi-karti-ekstre-listesi/<int:kart_id>/', views.kredi_karti_ekstre_listesi, name='kredi_karti_ekstre_listesi'),
    path('odeme-yap/<int:ekstre_id>/', views.odeme_yap, name='odeme_yap'),  # Yeni eklenen URL
    path('get-alt-kategoriler/', views.get_alt_kategoriler, name='get_alt_kategoriler'),
    path('duzenli-odeme-listesi/', views.duzenli_odeme_listesi, name='duzenli_odeme_listesi'),
    path('duzenli-odeme-ekstre-listesi/<int:duzenli_odeme_id>/', views.duzenli_odeme_ekstre_listesi, name='duzenli_odeme_ekstre_listesi'),
    path('duzenli-odeme-yap/<int:ekstre_id>/', views.duzenli_odeme_yap, name='duzenli_odeme_yap'),
    path('gelir-kategori-listesi/', views.gelir_kategori_listesi, name='gelir_kategori_listesi'),  # Yeni rota
    path('gider-kategori-listesi/', views.gider_kategori_listesi, name='gider_kategori_listesi'),  # Yeni rota
    path('analiz/', views.analiz, name='analiz'),
    path('toplu-ekstre-olustur/', views.toplu_ekstre_olustur, name='toplu_ekstre_olustur'),




]