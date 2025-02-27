from django import forms
from .models import Gelir, Gider, KrediKarti, DüzenliÖdeme, GelirKategori, GiderKategori
from django.contrib.auth.models import User

class GiderForm(forms.ModelForm):
    üst_kategori = forms.ModelChoiceField(
        queryset=GiderKategori.objects.filter(üst_kategori__isnull=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_üst_kategori'}),
        label="Üst Kategori"
    )

    class Meta:
        model = Gider
        fields = ['kullanıcı', 'üst_kategori', 'kategori', 'miktar', 'para_birimi', 'açıklama', 'tarih']
        widgets = {
            'kullanıcı': forms.Select(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control', 'id': 'id_kategori'}),
            'miktar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'para_birimi': forms.Select(attrs={'class': 'form-control'}),
            'açıklama': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'tarih': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kullanıcı'].queryset = User.objects.all()
        self.fields['kategori'].queryset = GiderKategori.objects.filter(üst_kategori__isnull=False)
        self.fields['kategori'].required = False

    def clean(self):
        cleaned_data = super().clean()
        üst_kategori = cleaned_data.get('üst_kategori')
        kategori = cleaned_data.get('kategori')

        # Üst kategori seçilmiş ve alt kategori boşsa, üst kategoriyi kategori olarak ata
        if üst_kategori and not kategori:
            cleaned_data['kategori'] = üst_kategori
        # Alt kategori seçilmişse, üst kategoriyle uyumlu mu kontrol et
        elif kategori and üst_kategori and kategori.üst_kategori != üst_kategori:
            raise forms.ValidationError("Seçilen alt kategori, üst kategori ile uyuşmuyor.")

        return cleaned_data

# Diğer formlar aynı kalabilir (GelirForm, KrediKartiForm, vb.)
class GelirForm(forms.ModelForm):
    üst_kategori = forms.ModelChoiceField(
        queryset=GelirKategori.objects.filter(üst_kategori__isnull=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_üst_kategori'}),
        label="Üst Kategori"
    )

    class Meta:
        model = Gelir
        fields = ['kullanıcı', 'üst_kategori', 'kategori', 'miktar', 'para_birimi', 'açıklama', 'tarih']
        widgets = {
            'kullanıcı': forms.Select(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control', 'id': 'id_kategori'}),
            'miktar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'para_birimi': forms.Select(attrs={'class': 'form-control'}),
            'açıklama': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'tarih': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kullanıcı'].queryset = User.objects.all()
        self.fields['kategori'].queryset = GelirKategori.objects.filter(üst_kategori__isnull=False)
        self.fields['kategori'].required = False

    def clean(self):
        cleaned_data = super().clean()
        üst_kategori = cleaned_data.get('üst_kategori')
        kategori = cleaned_data.get('kategori')
        if kategori and üst_kategori and kategori.üst_kategori != üst_kategori:
            raise forms.ValidationError("Seçilen alt kategori, üst kategori ile uyuşmuyor.")
        # Üst kategori seçilmiş ve alt kategori boşsa, üst kategoriyi kategori olarak ata
        if üst_kategori and not kategori:
            cleaned_data['kategori'] = üst_kategori
        return cleaned_data

class KrediKartiForm(forms.ModelForm):
    class Meta:
        model = KrediKarti
        fields = ['kullanıcı', 'isim', 'toplam_borc', 'limit', 'son_ödeme_günü', 'asgari_ödeme_yüzdesi']
        widgets = {
            'kullanıcı': forms.Select(attrs={'class': 'form-control'}),
            'isim': forms.TextInput(attrs={'class': 'form-control'}),
            'toplam_borc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'son_ödeme_günü': forms.NumberInput(attrs={'class': 'form-control'}),
            'asgari_ödeme_yüzdesi': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kullanıcı'].queryset = User.objects.all()

class DüzenliÖdemeForm(forms.ModelForm):
    üst_kategori = forms.ModelChoiceField(
        queryset=GiderKategori.objects.filter(üst_kategori__isnull=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_üst_kategori'}),
        label="Üst Kategori"
    )

    class Meta:
        model = DüzenliÖdeme
        fields = ['kullanıcı', 'üst_kategori', 'kategori', 'açıklama', 'miktar', 'para_birimi', 'ödeme_günü']
        widgets = {
            'kullanıcı': forms.Select(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control', 'id': 'id_kategori'}),
            'açıklama': forms.TextInput(attrs={'class': 'form-control'}),
            'miktar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'para_birimi': forms.Select(attrs={'class': 'form-control'}),
            'ödeme_günü': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kullanıcı'].queryset = User.objects.all()
        self.fields['kategori'].queryset = GiderKategori.objects.filter(üst_kategori__isnull=False)
        self.fields['kategori'].required = False

    def clean(self):
        cleaned_data = super().clean()
        üst_kategori = cleaned_data.get('üst_kategori')
        kategori = cleaned_data.get('kategori')
        if kategori and üst_kategori and kategori.üst_kategori != üst_kategori:
            raise forms.ValidationError("Seçilen alt kategori, üst kategori ile uyuşmuyor.")
        # Üst kategori seçilmiş ve alt kategori boşsa, üst kategoriyi kategori olarak ata
        if üst_kategori and not kategori:
            cleaned_data['kategori'] = üst_kategori
        return cleaned_data

# finans/forms.py
from django import forms
from .models import GelirKategori, GiderKategori

class GelirKategoriForm(forms.ModelForm):
    üst_kategori_adı = forms.CharField(
        max_length=100,
        required=False,
        label="Yeni Üst Kategori Adı (İsteğe Bağlı)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Yeni üst kategori girin'}),
    )

    class Meta:
        model = GelirKategori
        fields = ['isim', 'üst_kategori']
        widgets = {
            'isim': forms.TextInput(attrs={'class': 'form-control'}),
            'üst_kategori': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        isim = cleaned_data.get('isim')
        üst_kategori = cleaned_data.get('üst_kategori')
        üst_kategori_adı = cleaned_data.get('üst_kategori_adı')

        # Eğer üst_kategori_adı girilmişse, yeni bir üst kategori oluştur
        if üst_kategori_adı and not üst_kategori:
            üst_kategori, created = GelirKategori.objects.get_or_create(
                isim=üst_kategori_adı,
                üst_kategori=None  # Bu bir ana kategori olacak
            )
            cleaned_data['üst_kategori'] = üst_kategori

        return cleaned_data

class GiderKategoriForm(forms.ModelForm):
    üst_kategori_adı = forms.CharField(
        max_length=100,
        required=False,
        label="Yeni Üst Kategori Adı (İsteğe Bağlı)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Yeni üst kategori girin'}),
    )

    class Meta:
        model = GiderKategori
        fields = ['isim', 'üst_kategori']
        widgets = {
            'isim': forms.TextInput(attrs={'class': 'form-control'}),
            'üst_kategori': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        isim = cleaned_data.get('isim')
        üst_kategori = cleaned_data.get('üst_kategori')
        üst_kategori_adı = cleaned_data.get('üst_kategori_adı')

        # Eğer üst_kategori_adı girilmişse, yeni bir üst kategori oluştur
        if üst_kategori_adı and not üst_kategori:
            üst_kategori, created = GiderKategori.objects.get_or_create(
                isim=üst_kategori_adı,
                üst_kategori=None  # Bu bir ana kategori olacak
            )
            cleaned_data['üst_kategori'] = üst_kategori

        return cleaned_data
    class Meta:
        model = GiderKategori
        fields = ['isim', 'üst_kategori']
        widgets = {
            'isim': forms.TextInput(attrs={'class': 'form-control'}),
            'üst_kategori': forms.Select(attrs={'class': 'form-control'}),
        }