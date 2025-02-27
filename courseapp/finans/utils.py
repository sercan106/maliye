# finans/utils.py
import decimal  # decimal modülünü tam import et
from decimal import Decimal  # Decimal sınıfını ayrı import et
from bs4 import BeautifulSoup
import requests
def kurlari_al():
    # Kullanılacak bağlantılar
    ruble_bağlantısı = "https://kur.altin.in/kur/rus-rublesi"
    altın_bağlantısı = "https://kur.altin.in/kur/altin"  # Altın için doğru sayfa
    banka_bağlantısı = "https://altin.in/"

    başlıklar = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    varsayılan_değer = Decimal('0.00')

    # Ruble verisini çekme
    ruble_cevap = requests.get(ruble_bağlantısı, headers=başlıklar)
    ruble_soup = BeautifulSoup(ruble_cevap.content, "html.parser")
    ruble_öge = ruble_soup.select_one('#icerik > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > ul > li:nth-child(2)')
    ruble_tl = Decimal(ruble_öge.text.strip().replace(",", ".")) if ruble_öge and ruble_öge.text.strip() else varsayılan_değer

    # Altın verisini çekme (yeni bağlantı ve XPath'e göre)
    altın_cevap = requests.get(altın_bağlantısı, headers=başlıklar)
    altın_soup = BeautifulSoup(altın_cevap.content, "html.parser")
    altın_öge = altın_soup.select_one('#icerik > div:nth-child(1) > div:nth-child(2) > div:nth-child(4) > ul > li:nth-child(2)')  # XPath'i CSS'e çevirdim
    altın_tl = Decimal(altın_öge.text.strip().replace(",", ".")) if altın_öge and altın_öge.text.strip() else varsayılan_değer

    # Dolar verisini çekme
    banka_cevap = requests.get(banka_bağlantısı, headers=başlıklar)
    banka_soup = BeautifulSoup(banka_cevap.content, "html.parser")
    dolar_öge = banka_soup.select_one('#dfiy')
    dolar_tl = Decimal(dolar_öge.text.strip().replace(",", ".")) if dolar_öge and dolar_öge.text.strip() else varsayılan_değer

    return altın_tl, dolar_tl, ruble_tl