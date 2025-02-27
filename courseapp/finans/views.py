from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Gelir, Gider, KrediKarti, KrediKartiEkstre, DüzenliÖdeme, DüzenliÖdemeEkstresi, GelirKategori, GiderKategori, KrediKartiÖdeme
from .forms import GelirForm, GelirKategoriForm, GiderForm, GiderKategoriForm, KrediKartiForm, DüzenliÖdemeForm
from django.db.models import Sum, Case, When, DecimalField
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from .utils import kurlari_al
import calendar

@login_required
def gelir_ekle(request):
    if request.method == 'POST':
        form = GelirForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gelir başarıyla eklendi!')
            return redirect('finans:anasayfa')
    else:
        form = GelirForm()
    return render(request, 'finans/gelir_ekle.html', {'form': form})

@login_required
def gelir_listesi(request):
    gelirler = Gelir.objects.all().order_by('-tarih')  # Kullanıcı sınırlaması zaten yoktu
    paginator = Paginator(gelirler, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'finans/gelir_listesi.html', context)

@login_required
def gider_ekle(request):
    if request.method == 'POST':
        form = GiderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gider başarıyla eklendi!')
            return redirect('finans:anasayfa')
    else:
        form = GiderForm()
    return render(request, 'finans/gider_ekle.html', {'form': form})

@login_required
def gider_listesi(request):
    giderler = Gider.objects.all().order_by('-tarih')  # Kullanıcı sınırlaması zaten yoktu
    paginator = Paginator(giderler, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'finans/gider_listesi.html', context)

@login_required
def kredi_karti_ekle(request):
    if request.method == 'POST':
        form = KrediKartiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kredi kartı başarıyla eklendi!')
            return redirect('finans:anasayfa')
    else:
        form = KrediKartiForm()
    return render(request, 'finans/kredi_karti_ekle.html', {'form': form})

@login_required
def duzenli_ödeme_ekle(request):
    if request.method == 'POST':
        form = DüzenliÖdemeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Düzenli ödeme başarıyla eklendi!')
            return redirect('finans:anasayfa')
    else:
        form = DüzenliÖdemeForm()
    return render(request, 'finans/duzenli_ödeme_ekle.html', {'form': form})

@login_required
def get_alt_kategoriler(request):
    ust_kategori_id = request.GET.get('ust_kategori_id')
    kategori_tipi = request.GET.get('kategori_tipi')
    if ust_kategori_id:
        if kategori_tipi == 'gelir':
            alt_kategoriler = GelirKategori.objects.filter(üst_kategori_id=ust_kategori_id).values('id', 'isim')
        else:
            alt_kategoriler = GiderKategori.objects.filter(üst_kategori_id=ust_kategori_id).values('id', 'isim')
    else:
        if kategori_tipi == 'gelir':
            alt_kategoriler = GelirKategori.objects.filter(üst_kategori__isnull=False).values('id', 'isim')
        else:
            alt_kategoriler = GiderKategori.objects.filter(üst_kategori__isnull=False).values('id', 'isim')
    return JsonResponse({'alt_kategoriler': list(alt_kategoriler)})

@login_required
def kredi_karti_listesi(request):
    kartlar = KrediKarti.objects.all().select_related('kullanıcı').prefetch_related('kredikartiekstre_set')
    toplam_borc = KrediKarti.objects.aggregate(Sum('toplam_borc'))['toplam_borc__sum'] or 0
    toplam_limit = KrediKarti.objects.aggregate(Sum('limit'))['limit__sum'] or 0
    toplam_asgari_tutar = KrediKartiEkstre.objects.aggregate(Sum('asgari_tutar'))['asgari_tutar__sum'] or 0
    
    kart_verileri = []
    for kart in kartlar:
        kart_asgari_tutar = KrediKartiEkstre.objects.filter(kredi_karti=kart).aggregate(Sum('asgari_tutar'))['asgari_tutar__sum'] or 0
        kart_verileri.append({
            'kart': kart,
            'asgari_tutar': kart_asgari_tutar,
        })
    
    context = {
        'kart_verileri': kart_verileri,
        'toplam_borc': toplam_borc,
        'toplam_limit': toplam_limit,
        'toplam_asgari_tutar': toplam_asgari_tutar,
    }
    return render(request, 'finans/kredi_karti_listesi.html', context)

@login_required
def kredi_karti_ekstre_listesi(request, kart_id):
    ekstreler = KrediKartiEkstre.objects.filter(kredi_karti_id=kart_id).select_related('kredi_karti__kullanıcı').order_by('-son_ödeme_tarihi')  # Kullanıcı sınırlaması zaten yoktu
    kart = KrediKarti.objects.get(id=kart_id)
    context = {
        'ekstreler': ekstreler,
        'kart': kart,
    }
    return render(request, 'finans/kredi_karti_ekstre_listesi.html', context)

@login_required
def odeme_yap(request, ekstre_id):
    ekstre = get_object_or_404(KrediKartiEkstre, id=ekstre_id)  # Kullanıcı sınırlaması kaldırıldı
    if request.method == 'POST':
        miktar = Decimal(request.POST.get('miktar', '0'))
        faiz = Decimal(request.POST.get('faiz', '0'))
        from_anasayfa = request.POST.get('from_anasayfa', 'false') == 'true'
        if not ekstre.ödendi_mi:
            KrediKartiÖdeme.objects.create(
                ödeme_durumu=ekstre,
                miktar=miktar,
                faiz=faiz,
                tarih=datetime.now().date(),
                para_birimi='TL'
            )
            messages.success(request, f'{ekstre.kredi_karti.isim} için ödeme başarıyla yapıldı! (Faiz: {faiz} TL)')
        if from_anasayfa:
            return redirect('finans:anasayfa')
        return redirect('finans:kredi_karti_ekstre_listesi', kart_id=ekstre.kredi_karti.id)
    return redirect('finans:kredi_karti_ekstre_listesi', kart_id=ekstre.kredi_karti.id)

@login_required
def duzenli_odeme_listesi(request):
    # Ödeme gününe göre sıralama (en küçükten en büyüğe)
    duzenli_odemeler = DüzenliÖdeme.objects.all().select_related('kullanıcı', 'kategori').order_by('ödeme_günü')
    context = {
        'duzenli_odemeler': duzenli_odemeler,
    }
    return render(request, 'finans/duzenli_odeme_listesi.html', context)

@login_required
def duzenli_odeme_ekstre_listesi(request, duzenli_odeme_id):
    duzenli_odeme = get_object_or_404(DüzenliÖdeme, id=duzenli_odeme_id)  # Kullanıcı sınırlaması zaten kaldırılmıştı
    ekstreler = DüzenliÖdemeEkstresi.objects.filter(düzenli_ödeme=duzenli_odeme).select_related('düzenli_ödeme')
    context = {
        'duzenli_odeme': duzenli_odeme,
        'ekstreler': ekstreler,
    }
    return render(request, 'finans/duzenli_odeme_ekstre_listesi.html', context)

@login_required
def duzenli_odeme_yap(request, ekstre_id):
    ekstre = get_object_or_404(DüzenliÖdemeEkstresi, id=ekstre_id)  # Kullanıcı sınırlaması kaldırıldı
    if request.method == "POST" and not ekstre.ödendi_mi:
        miktar = Decimal(request.POST.get("miktar", "0"))
        from_anasayfa = request.POST.get('from_anasayfa', 'false') == 'true'
        ekstre.ödendi_mi = True
        ekstre.save()
        
        kategori, _ = GiderKategori.objects.get_or_create(isim="Düzenli Ödeme")
        Gider.objects.create(
            kullanıcı=ekstre.düzenli_ödeme.kullanıcı,  # Ekstrenin bağlı olduğu düzenli ödemenin kullanıcısı
            kategori=kategori,
            miktar=miktar,
            para_birimi=ekstre.düzenli_ödeme.para_birimi,
            açıklama=f"{ekstre.düzenli_ödeme.açıklama} - Ödeme",
            tarih=datetime.now().date()
        )
        
        messages.success(request, f"{ekstre.düzenli_ödeme.açıklama} için ödeme başarıyla yapıldı!")
        if from_anasayfa:
            return redirect("finans:anasayfa")
        return redirect("finans:duzenli_odeme_ekstre_listesi", duzenli_odeme_id=ekstre.düzenli_ödeme.id)
    return redirect("finans:duzenli_odeme_ekstre_listesi", duzenli_odeme_id=ekstre.düzenli_ödeme.id)

@login_required
def toplu_ekstre_olustur(request):
    if request.method == 'POST':
        try:
            şuanki_tarih = timezone.now()
            şuanki_ay = şuanki_tarih.month
            şuanki_yıl = şuanki_tarih.year

            # Kredi Kartı Ekstreleri
            kredi_kartları = KrediKarti.objects.all()  # Kullanıcı sınırlaması kaldırıldı
            for kart in kredi_kartları:
                ekstre_var = KrediKartiEkstre.objects.filter(
                    kredi_karti=kart,
                    ay=şuanki_ay,
                    yıl=şuanki_yıl
                ).exists()
                if not ekstre_var:
                    ay_sonu = calendar.monthrange(şuanki_yıl, şuanki_ay)[1]
                    son_ödeme_günü = min(kart.son_ödeme_günü, ay_sonu)
                    son_ödeme_tarihi = şuanki_tarih.replace(day=son_ödeme_günü)
                    KrediKartiEkstre.objects.create(
                        kredi_karti=kart,
                        son_ödeme_tarihi=son_ödeme_tarihi,
                        asgari_tutar=kart.toplam_borc * (kart.asgari_ödeme_yüzdesi / 100),
                        ödendi_mi=False,
                        ay=şuanki_ay,
                        yıl=şuanki_yıl
                    )

            # Düzenli Ödeme Ekstreleri
            düzenli_ödemeler = DüzenliÖdeme.objects.all()  # Kullanıcı sınırlaması kaldırıldı
            for ödeme in düzenli_ödemeler:
                ekstre_var = DüzenliÖdemeEkstresi.objects.filter(
                    düzenli_ödeme=ödeme,
                    ay=şuanki_ay,
                    yıl=şuanki_yıl
                ).exists()
                if not ekstre_var:
                    ay_sonu = calendar.monthrange(şuanki_yıl, şuanki_ay)[1]
                    son_ödeme_günü = min(ödeme.ödeme_günü, ay_sonu)
                    son_ödeme_tarihi = şuanki_tarih.replace(day=son_ödeme_günü)
                    DüzenliÖdemeEkstresi.objects.create(
                        düzenli_ödeme=ödeme,
                        son_ödeme_tarihi=son_ödeme_tarihi,
                        ödendi_mi=False,
                        ay=şuanki_ay,
                        yıl=şuanki_yıl
                    )

            messages.success(request, "Toplu ekstreler başarıyla oluşturuldu.")
        except Exception as e:
            messages.error(request, f"Ekstre oluşturma hatası: {str(e)}")
    return redirect('finans:anasayfa')  # View adı toplu_ekstre_olustur, ancak anasayfa’ya yönlendirme





@login_required
def gelir_kategori_listesi(request):
    if request.method == 'POST':
        form = GelirKategoriForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gelir kategorisi başarıyla eklendi!')
            return redirect('finans:gelir_kategori_listesi')
    else:
        form = GelirKategoriForm()

    ust_kategoriler = GelirKategori.objects.filter(üst_kategori__isnull=True).order_by('isim')
    kategori_hiyerarsi = {ust: GelirKategori.objects.filter(üst_kategori=ust).order_by('isim') for ust in ust_kategoriler}

    context = {
        'kategori_hiyerarsi': kategori_hiyerarsi,
        'form': form,
    }
    return render(request, 'finans/gelir_kategori_listesi.html', context)

@login_required
def gider_kategori_listesi(request):
    if request.method == 'POST':
        form = GiderKategoriForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gider kategorisi başarıyla eklendi!')
            return redirect('finans:gider_kategori_listesi')
    else:
        form = GiderKategoriForm()

    ust_kategoriler = GiderKategori.objects.filter(üst_kategori__isnull=True).order_by('isim')
    kategori_hiyerarsi = {ust: GiderKategori.objects.filter(üst_kategori=ust).order_by('isim') for ust in ust_kategoriler}

    context = {
        'kategori_hiyerarsi': kategori_hiyerarsi,
        'form': form,
    }
    return render(request, 'finans/gider_kategori_listesi.html', context)






'''
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from datetime import timedelta
from .utils import kurlari_al
from .models import Gelir, Gider, KrediKartiEkstre, DüzenliÖdemeEkstresi
import locale

@login_required
def anasayfa(request):  
    şu_an = timezone.now()
    # Mevcut yıl ve ay
    mevcut_yıl = şu_an.year
    mevcut_ay = şu_an.month

    # Ay isimlerini içeren bir sözlük
    aylar = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
        7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }

    # Türkçe ay adını değişkene ata
    şimdiki_ay = aylar[mevcut_ay]


    # Ödenmemiş düzenli ödeme ekstrelerinin toplam tutarı
    odemesi_yapilmamis_duzenli_tutar = Decimal('0.00')
    odemesi_yapilmamis_duzenli_ekstreler = DüzenliÖdemeEkstresi.objects.filter(
        ay=mevcut_ay,
        yıl=mevcut_yıl,
        ödendi_mi=False
    )
    for ekstre in odemesi_yapilmamis_duzenli_ekstreler:
        odemesi_yapilmamis_duzenli_tutar += ekstre.düzenli_ödeme.miktar

    # Ödenmemiş kredi kartı ekstrelerinin asgari tutar toplamı
    odemesi_yapilmamis_kredi_asgari_tutar = Decimal('0.00')
    odemesi_yapilmamis_kredi_ekstreleri = KrediKartiEkstre.objects.filter(
        ay=mevcut_ay,
        yıl=mevcut_yıl,
        ödendi_mi=False
    )
    for ekstre in odemesi_yapilmamis_kredi_ekstreleri:
        odemesi_yapilmamis_kredi_asgari_tutar += ekstre.asgari_tutar

    aylık_toplam_ödemeler=odemesi_yapilmamis_duzenli_tutar+odemesi_yapilmamis_kredi_asgari_tutar
    # Sonuçları ayrı değişkenler olarak döndür
 


    # Aylık gelir ve giderleri tek sorguda toplama
    aylık_gelirler = Gelir.objects.filter(tarih__year=mevcut_yıl, tarih__month=mevcut_ay).values('para_birimi').annotate(toplam=Sum('miktar')).order_by()
    aylık_giderler = Gider.objects.filter(tarih__year=mevcut_yıl, tarih__month=mevcut_ay).values('para_birimi').annotate(toplam=Sum('miktar')).order_by()

    # Toplam gelir ve giderleri tek sorguda toplama
    toplam_gelirler = Gelir.objects.values('para_birimi').annotate(toplam=Sum('miktar')).order_by()
    toplam_giderler = Gider.objects.values('para_birimi').annotate(toplam=Sum('miktar')).order_by()

    # Sözlükler oluşturup varsayılan değerleri 0.00 olarak ayarlama
    aylık_gelir_dict = {entry['para_birimi']: entry['toplam'] for entry in aylık_gelirler}
    aylık_gider_dict = {entry['para_birimi']: entry['toplam'] for entry in aylık_giderler}
    toplam_gelir_dict = {entry['para_birimi']: entry['toplam'] for entry in toplam_gelirler}
    toplam_gider_dict = {entry['para_birimi']: entry['toplam'] for entry in toplam_giderler}

    # Aylık değişkenler
    aylık_tl_gelir = aylık_gelir_dict.get('TL', Decimal('0.00'))
    aylık_tl_gider = aylık_gider_dict.get('TL', Decimal('0.00'))
    aylık_usd_gelir = aylık_gelir_dict.get('USD', Decimal('0.00'))
    aylık_usd_gider = aylık_gider_dict.get('USD', Decimal('0.00'))
    aylık_rub_gelir = aylık_gelir_dict.get('RUB', Decimal('0.00'))
    aylık_rub_gider = aylık_gider_dict.get('RUB', Decimal('0.00'))
    aylık_gold_gelir = aylık_gelir_dict.get('GOLD', Decimal('0.00'))
    aylık_gold_gider = aylık_gider_dict.get('GOLD', Decimal('0.00'))

    aylık_bakiye_usd = aylık_usd_gelir - aylık_usd_gider
    aylık_bakiye_tl = aylık_tl_gelir - aylık_tl_gider
    aylık_bakiye_gold = aylık_gold_gelir - aylık_gold_gider
    aylık_bakiye_rub = aylık_rub_gelir - aylık_rub_gider

    # Toplam değişkenler
    toplam_tl_gelir = toplam_gelir_dict.get('TL', Decimal('0.00'))
    toplam_tl_gider = toplam_gider_dict.get('TL', Decimal('0.00'))
    toplam_usd_gelir = toplam_gelir_dict.get('USD', Decimal('0.00'))
    toplam_usd_gider = toplam_gider_dict.get('USD', Decimal('0.00'))
    toplam_rub_gelir = toplam_gelir_dict.get('RUB', Decimal('0.00'))
    toplam_rub_gider = toplam_gider_dict.get('RUB', Decimal('0.00'))
    toplam_gold_gelir = toplam_gelir_dict.get('GOLD', Decimal('0.00'))
    toplam_gold_gider = toplam_gider_dict.get('GOLD', Decimal('0.00'))

    toplam_bakiye_tl = toplam_tl_gelir - toplam_tl_gider
    toplam_bakiye_usd = toplam_usd_gelir - toplam_usd_gider
    toplam_bakiye_rub = toplam_rub_gelir - toplam_rub_gider
    toplam_bakiye_gold = toplam_gold_gelir - toplam_gold_gider

    # Kurları çekme
    altın_tl, dolar_tl, ruble_tl = kurlari_al()

    # Aylık ve toplam bakiye hesaplama (TL cinsinden toplam)
    tüm_aylık_bakiye_toplam_tl = (aylık_tl_gelir - aylık_tl_gider) + (aylık_usd_gelir - aylık_usd_gider) * dolar_tl + (aylık_rub_gelir - aylık_rub_gider) * ruble_tl + (aylık_gold_gelir - aylık_gold_gider) * altın_tl
    tüm_toplam_bakiye_tl = (toplam_tl_gelir - toplam_tl_gider) + (toplam_usd_gelir - toplam_usd_gider) * dolar_tl + (toplam_rub_gelir - toplam_rub_gider) * ruble_tl + (toplam_gold_gelir - toplam_gold_gider) * altın_tl

    tüm_aylık_gelir_toplam_tl=(aylık_tl_gelir ) + (aylık_usd_gelir ) * dolar_tl + (aylık_rub_gelir ) * ruble_tl + (aylık_gold_gelir ) * altın_tl
    tüm_aylık_gider_toplam_tl=(aylık_tl_gider ) + (aylık_usd_gider ) * dolar_tl + (aylık_rub_gider ) * ruble_tl + (aylık_gold_gider ) * altın_tl


    # Yaklaşan ödemeler
    baslangic = şu_an.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    bitis = (baslangic + timedelta(days=32)).replace(day=1)
    
    kredi_odemeleri = KrediKartiEkstre.objects.filter(
        son_ödeme_tarihi__gte=baslangic,
        son_ödeme_tarihi__lt=bitis,
        ödendi_mi=False
    ).order_by('son_ödeme_tarihi')
    
    duzenli_odemeler = DüzenliÖdemeEkstresi.objects.filter(
        son_ödeme_tarihi__gte=baslangic,
        son_ödeme_tarihi__lt=bitis,
        ödendi_mi=False
    ).order_by('son_ödeme_tarihi')

    # Son işlemler
    son_gelirler = Gelir.objects.filter(kullanıcı=request.user).order_by('-tarih')[:5]
    son_giderler = Gider.objects.filter(kullanıcı=request.user).order_by('-tarih')[:5]

    # Template’e aktarılacak veriler
    context = {
        'aylık_tl_gelir': aylık_tl_gelir,
        'aylık_tl_gider': aylık_tl_gider,
        'aylık_usd_gelir': aylık_usd_gelir,
        'aylık_usd_gider': aylık_usd_gider,
        'aylık_rub_gelir': aylık_rub_gelir,
        'aylık_rub_gider': aylık_rub_gider,
        'aylık_gold_gelir': aylık_gold_gelir,
        'aylık_gold_gider': aylık_gold_gider,

        'toplam_tl_gelir': toplam_tl_gelir,
        'toplam_tl_gider': toplam_tl_gider,
        'toplam_usd_gelir': toplam_usd_gelir,
        'toplam_usd_gider': toplam_usd_gider,
        'toplam_rub_gelir': toplam_rub_gelir,
        'toplam_rub_gider': toplam_rub_gider,
        'toplam_gold_gelir': toplam_gold_gelir,
        'toplam_gold_gider': toplam_gold_gider,

        'altın_kur': altın_tl,  # Kurları ayırt etmek için isim değişikliği
        'dolar_kur': dolar_tl,
        'ruble_kur': ruble_tl,

        'tüm_aylık_bakiye_toplam_tl': tüm_aylık_bakiye_toplam_tl,
        'tüm_toplam_bakiye_tl': tüm_toplam_bakiye_tl,

        'toplam_bakiye_tl': toplam_bakiye_tl,
        'toplam_bakiye_usd': toplam_bakiye_usd,
        'toplam_bakiye_gold': toplam_bakiye_gold,
        'toplam_bakiye_rub': toplam_bakiye_rub,

        'aylık_bakiye_tl': aylık_bakiye_tl,
        'aylık_bakiye_gold': aylık_bakiye_gold,
        'aylık_bakiye_rub': aylık_bakiye_rub,
        'aylık_bakiye_usd': aylık_bakiye_usd,

        'tüm_aylık_gelir_toplam_tl':tüm_aylık_gelir_toplam_tl,
        'tüm_aylık_gider_toplam_tl':tüm_aylık_gider_toplam_tl,

        'duzenli_odemeler_toplam': odemesi_yapilmamis_duzenli_tutar,
        'kredi_karti_asgari_toplam': odemesi_yapilmamis_kredi_asgari_tutar,
        'aylık_toplam_ödemeler': aylık_toplam_ödemeler,

        'kredi_odemeleri': kredi_odemeleri,
        'duzenli_odemeler': duzenli_odemeler,
        'son_gelirler': son_gelirler,
        'son_giderler': son_giderler,
        'current_month': şu_an.strftime("%B %Y"),
        'today': şu_an.date(),
        'şimdiki_ay': şimdiki_ay,
    }

    return render(request, 'finans/anasayfa.html', context)'''
































@login_required
def anasayfa(request):  

    şu_an = timezone.now()
    mevcut_yıl = şu_an.year
    mevcut_ay = şu_an.month

    aylar = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
        7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }
    şimdiki_ay = aylar[mevcut_ay]

    # Ödenmemiş düzenli ödemeler ve kredi kartı ekstreleri (kullanıcı sınırlaması kaldırıldı)
    odemesi_yapilmamis_duzenli_tutar = DüzenliÖdemeEkstresi.objects.filter(
        ay=mevcut_ay,
        yıl=mevcut_yıl,
        ödendi_mi=False
    ).aggregate(
        toplam=Sum('düzenli_ödeme__miktar', output_field=DecimalField())
    )['toplam'] or Decimal('0.00')

    odemesi_yapilmamis_kredi_asgari_tutar = KrediKartiEkstre.objects.filter(
        ay=mevcut_ay,
        yıl=mevcut_yıl,
        ödendi_mi=False
    ).aggregate(
        toplam=Sum('asgari_tutar', output_field=DecimalField())
    )['toplam'] or Decimal('0.00')

    aylık_toplam_ödemeler = odemesi_yapilmamis_duzenli_tutar + odemesi_yapilmamis_kredi_asgari_tutar

    # Aylık ve toplam gelir/giderler (kullanıcı sınırlaması kaldırıldı)
    gelir_queryset = Gelir.objects.all()
    gider_queryset = Gider.objects.all()

    aylık_filtre = {'tarih__year': mevcut_yıl, 'tarih__month': mevcut_ay}

    aylık_gelirler = gelir_queryset.filter(**aylık_filtre).aggregate(
        tl_gelir=Sum(Case(When(para_birimi='TL', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        usd_gelir=Sum(Case(When(para_birimi='USD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        rub_gelir=Sum(Case(When(para_birimi='RUB', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        gold_gelir=Sum(Case(When(para_birimi='GOLD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
    )

    aylık_giderler = gider_queryset.filter(**aylık_filtre).aggregate(
        tl_gider=Sum(Case(When(para_birimi='TL', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        usd_gider=Sum(Case(When(para_birimi='USD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        rub_gider=Sum(Case(When(para_birimi='RUB', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        gold_gider=Sum(Case(When(para_birimi='GOLD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
    )

    toplam_gelirler = gelir_queryset.aggregate(
        tl_gelir=Sum(Case(When(para_birimi='TL', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        usd_gelir=Sum(Case(When(para_birimi='USD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        rub_gelir=Sum(Case(When(para_birimi='RUB', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        gold_gelir=Sum(Case(When(para_birimi='GOLD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
    )

    toplam_giderler = gider_queryset.aggregate(
        tl_gider=Sum(Case(When(para_birimi='TL', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        usd_gider=Sum(Case(When(para_birimi='USD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        rub_gider=Sum(Case(When(para_birimi='RUB', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
        gold_gider=Sum(Case(When(para_birimi='GOLD', then='miktar'), output_field=DecimalField()), default=Decimal('0.00')),
    )

    # Aylık değişkenler
    aylık_tl_gelir = aylık_gelirler['tl_gelir']
    aylık_tl_gider = aylık_giderler['tl_gider']
    aylık_usd_gelir = aylık_gelirler['usd_gelir']
    aylık_usd_gider = aylık_giderler['usd_gider']
    aylık_rub_gelir = aylık_gelirler['rub_gelir']
    aylık_rub_gider = aylık_giderler['rub_gider']
    aylık_gold_gelir = aylık_gelirler['gold_gelir']
    aylık_gold_gider = aylık_giderler['gold_gider']

    aylık_bakiye_usd = aylık_usd_gelir - aylık_usd_gider
    aylık_bakiye_tl = aylık_tl_gelir - aylık_tl_gider
    aylık_bakiye_gold = aylık_gold_gelir - aylık_gold_gider
    aylık_bakiye_rub = aylık_rub_gelir - aylık_rub_gider

    # Toplam değişkenler
    toplam_tl_gelir = toplam_gelirler['tl_gelir']
    toplam_tl_gider = toplam_giderler['tl_gider']
    toplam_usd_gelir = toplam_gelirler['usd_gelir']
    toplam_usd_gider = toplam_giderler['usd_gider']
    toplam_rub_gelir = toplam_gelirler['rub_gelir']
    toplam_rub_gider = toplam_giderler['rub_gider']
    toplam_gold_gelir = toplam_gelirler['gold_gelir']
    toplam_gold_gider = toplam_giderler['gold_gider']

    toplam_bakiye_tl = toplam_tl_gelir - toplam_tl_gider
    toplam_bakiye_usd = toplam_usd_gelir - toplam_usd_gider
    toplam_bakiye_rub = toplam_rub_gelir - toplam_rub_gider
    toplam_bakiye_gold = toplam_gold_gelir - toplam_gold_gider

    # Kurları çekme
    altın_tl, dolar_tl, ruble_tl = kurlari_al()

    # TL cinsinden toplamlar
    tüm_aylık_bakiye_toplam_tl = aylık_bakiye_tl + aylık_bakiye_usd * dolar_tl + aylık_bakiye_rub * ruble_tl + aylık_bakiye_gold * altın_tl
    tüm_toplam_bakiye_tl = toplam_bakiye_tl + toplam_bakiye_usd * dolar_tl + toplam_bakiye_rub * ruble_tl + toplam_bakiye_gold * altın_tl
    tüm_aylık_gelir_toplam_tl = aylık_tl_gelir + aylık_usd_gelir * dolar_tl + aylık_rub_gelir * ruble_tl + aylık_gold_gelir * altın_tl
    tüm_aylık_gider_toplam_tl = aylık_tl_gider + aylık_usd_gider * dolar_tl + aylık_rub_gider * ruble_tl + aylık_gold_gider * altın_tl

    # Yaklaşan ödemeler (kullanıcı sınırlaması kaldırıldı)
    baslangic = şu_an.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    bitis = (baslangic + timedelta(days=32)).replace(day=1)

    kredi_odemeleri = KrediKartiEkstre.objects.filter(
        son_ödeme_tarihi__gte=baslangic,
        son_ödeme_tarihi__lt=bitis,
        ödendi_mi=False
    ).order_by('-son_ödeme_tarihi')

    duzenli_odemeler = DüzenliÖdemeEkstresi.objects.filter(
        son_ödeme_tarihi__gte=baslangic,
        son_ödeme_tarihi__lt=bitis,
        ödendi_mi=False
    ).order_by('-son_ödeme_tarihi')

    # Kalan gün hesaplama ve metin hazırlama
    for odeme in kredi_odemeleri:
        kalan_gun = (odeme.son_ödeme_tarihi - şu_an.date()).days
        odeme.kalan_gun_metni = f"{abs(kalan_gun)} gün geçti" if kalan_gun < 0 else f"{kalan_gun} gün"
        odeme.kalan_gun = kalan_gun

    for odeme in duzenli_odemeler:
        kalan_gun = (odeme.son_ödeme_tarihi - şu_an.date()).days
        odeme.kalan_gun_metni = f"{abs(kalan_gun)} gün geçti" if kalan_gun < 0 else f"{kalan_gun} gün"
        odeme.kalan_gun = kalan_gun

    # Son işlemler (kullanıcı sınırlaması kaldırıldı)
    son_gelirler = gelir_queryset.order_by('-tarih')[:5]
    son_giderler = gider_queryset.order_by('-tarih')[:5]

    context = {
        'aylık_tl_gelir': aylık_tl_gelir,
        'aylık_tl_gider': aylık_tl_gider,
        'aylık_usd_gelir': aylık_usd_gelir,
        'aylık_usd_gider': aylık_usd_gider,
        'aylık_rub_gelir': aylık_rub_gelir,
        'aylık_rub_gider': aylık_rub_gider,
        'aylık_gold_gelir': aylık_gold_gelir,
        'aylık_gold_gider': aylık_gold_gider,

        'toplam_tl_gelir': toplam_tl_gelir,
        'toplam_tl_gider': toplam_tl_gider,
        'toplam_usd_gelir': toplam_usd_gelir,
        'toplam_usd_gider': toplam_usd_gider,
        'toplam_rub_gelir': toplam_rub_gelir,
        'toplam_rub_gider': toplam_rub_gider,
        'toplam_gold_gelir': toplam_gold_gelir,
        'toplam_gold_gider': toplam_gold_gider,

        'altın_kur': altın_tl,
        'dolar_kur': dolar_tl,
        'ruble_kur': ruble_tl,

        'tüm_aylık_bakiye_toplam_tl': tüm_aylık_bakiye_toplam_tl,
        'tüm_toplam_bakiye_tl': tüm_toplam_bakiye_tl,

        'toplam_bakiye_tl': toplam_bakiye_tl,
        'toplam_bakiye_usd': toplam_bakiye_usd,
        'toplam_bakiye_gold': toplam_bakiye_gold,
        'toplam_bakiye_rub': toplam_bakiye_rub,

        'aylık_bakiye_tl': aylık_bakiye_tl,
        'aylık_bakiye_gold': aylık_bakiye_gold,
        'aylık_bakiye_rub': aylık_bakiye_rub,
        'aylık_bakiye_usd': aylık_bakiye_usd,

        'tüm_aylık_gelir_toplam_tl': tüm_aylık_gelir_toplam_tl,
        'tüm_aylık_gider_toplam_tl': tüm_aylık_gider_toplam_tl,

        'duzenli_odemeler_toplam': odemesi_yapilmamis_duzenli_tutar,
        'kredi_karti_asgari_toplam': odemesi_yapilmamis_kredi_asgari_tutar,
        'aylık_toplam_ödemeler': aylık_toplam_ödemeler,

        'kredi_odemeleri': kredi_odemeleri,
        'duzenli_odemeler': duzenli_odemeler,
        'son_gelirler': son_gelirler,
        'son_giderler': son_giderler,
        'current_month': şu_an.strftime("%B %Y"),
        'today': şu_an.date(),
        'şimdiki_ay': şimdiki_ay,
    }

    return render(request, 'finans/anasayfa.html', context)


    






from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Case, When, DecimalField, F, ExpressionWrapper
from .models import Gelir, Gider, GelirKategori, GiderKategori
from django.contrib.auth.models import User
from django.utils import timezone
import json
from datetime import datetime
from .utils import kurlari_al

@login_required
def analiz(request):
    altın_tl, dolar_tl, ruble_tl = kurlari_al()
    kur_map = {'TL': 1, 'USD': dolar_tl, 'GOLD': altın_tl, 'RUB': ruble_tl}
    aylar_tr = {1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
                7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'}

    kullanicilar = User.objects.all()
    kullanici_listesi = {k.username: k.id for k in kullanicilar}
    gelir_kategoriler = GelirKategori.objects.all()
    gider_kategoriler = GiderKategori.objects.all()
    kategori_listesi = {f"{kat.isim} (Gelir)": kat.id for kat in gelir_kategoriler}  # Gelir/Gider ayrımı geri eklendi
    kategori_listesi.update({f"{kat.isim} (Gider)": kat.id for kat in gider_kategoriler})

    gelir_aylar = Gelir.objects.values('tarih__year', 'tarih__month').distinct()
    gider_aylar = Gider.objects.values('tarih__year', 'tarih__month').distinct()
    aylar = set()
    for ay in list(gelir_aylar) + list(gider_aylar):
        aylar.add((ay['tarih__year'], ay['tarih__month']))
    ay_listesi = sorted([(y, m, f"{aylar_tr[m]} {y}") for y, m in aylar], reverse=True)

    tum_veriler = {}
    for kullanici in kullanicilar:
        tum_veriler[kullanici.username] = {}
        for y, m, ay_adı in ay_listesi + [(None, None, 'Tüm Zamanlar')]:
            ay_filtresi = {} if y is None else {'tarih__year': y, 'tarih__month': m}
            gelir_toplam = Gelir.objects.filter(kullanıcı=kullanici, **ay_filtresi).aggregate(
                toplam=Sum(ExpressionWrapper(
                    Case(
                        When(para_birimi='TL', then=F('miktar')),
                        When(para_birimi='USD', then=F('miktar') * dolar_tl),
                        When(para_birimi='GOLD', then=F('miktar') * altın_tl),
                        When(para_birimi='RUB', then=F('miktar') * ruble_tl),
                        default=0,
                        output_field=DecimalField()
                    ),
                    output_field=DecimalField()
                ))
            )['toplam'] or 0
            gider_toplam = Gider.objects.filter(kullanıcı=kullanici, **ay_filtresi).aggregate(
                toplam=Sum(ExpressionWrapper(
                    Case(
                        When(para_birimi='TL', then=F('miktar')),
                        When(para_birimi='USD', then=F('miktar') * dolar_tl),
                        When(para_birimi='GOLD', then=F('miktar') * altın_tl),
                        When(para_birimi='RUB', then=F('miktar') * ruble_tl),
                        default=0,
                        output_field=DecimalField()
                    ),
                    output_field=DecimalField()
                ))
            )['toplam'] or 0
            tum_veriler[kullanici.username][ay_adı] = {
                'gelir': {},
                'gider': {},
                'toplam_gelir': float(gelir_toplam),
                'toplam_gider': float(gider_toplam),
            }
            # Gelir kategorileri
            for kat in gelir_kategoriler:
                kat_toplam = Gelir.objects.filter(kullanıcı=kullanici, kategori=kat, **ay_filtresi).aggregate(
                    toplam=Sum(ExpressionWrapper(
                        Case(
                            When(para_birimi='TL', then=F('miktar')),
                            When(para_birimi='USD', then=F('miktar') * dolar_tl),
                            When(para_birimi='GOLD', then=F('miktar') * altın_tl),
                            When(para_birimi='RUB', then=F('miktar') * ruble_tl),
                            default=0,
                            output_field=DecimalField()
                        ),
                        output_field=DecimalField()
                    ))
                )['toplam'] or 0
                # Üst kategori varsa üstü, yoksa kendi ismi
                kat_isim = kat.üst_kategori.isim if kat.üst_kategori else kat.isim
                if kat_isim in tum_veriler[kullanici.username][ay_adı]['gelir']:
                    tum_veriler[kullanici.username][ay_adı]['gelir'][kat_isim] += float(kat_toplam)
                else:
                    tum_veriler[kullanici.username][ay_adı]['gelir'][kat_isim] = float(kat_toplam)
            # Gider kategorileri
            for kat in gider_kategoriler:
                kat_toplam = Gider.objects.filter(kullanıcı=kullanici, kategori=kat, **ay_filtresi).aggregate(
                    toplam=Sum(ExpressionWrapper(
                        Case(
                            When(para_birimi='TL', then=F('miktar')),
                            When(para_birimi='USD', then=F('miktar') * dolar_tl),
                            When(para_birimi='GOLD', then=F('miktar') * altın_tl),
                            When(para_birimi='RUB', then=F('miktar') * ruble_tl),
                            default=0,
                            output_field=DecimalField()
                        ),
                        output_field=DecimalField()
                    ))
                )['toplam'] or 0
                # Üst kategori varsa üstü, yoksa kendi ismi
                kat_isim = kat.üst_kategori.isim if kat.üst_kategori else kat.isim
                if kat_isim in tum_veriler[kullanici.username][ay_adı]['gider']:
                    tum_veriler[kullanici.username][ay_adı]['gider'][kat_isim] += float(kat_toplam)
                else:
                    tum_veriler[kullanici.username][ay_adı]['gider'][kat_isim] = float(kat_toplam)

    context = {
        'tum_veriler': json.dumps(tum_veriler),
        'kullanici_listesi': kullanici_listesi,
        'kategori_listesi': kategori_listesi,
        'ay_listesi': [(ay_adı, ay_adı) for _, _, ay_adı in ay_listesi] + [('Tüm Zamanlar', 'Tüm Zamanlar')],
        'mevcut_ay_adı': timezone.now().strftime('%B %Y').replace('February', 'Şubat').replace('January', 'Ocak')
    }
    return render(request, 'finans/analiz.html', context)