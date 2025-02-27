from django.urls import path
from . import views

app_name = 'hesap'

urlpatterns = [
    path('kayit/', views.kayit, name='kayit'),
    path('giris/', views.giris, name='giris'),
    path('cikis/', views.cikis, name='cikis'),
]