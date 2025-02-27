from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def kayit(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu ve giriş yapıldı!')
            return redirect('finans:anasayfa')
        else:
            messages.error(request, 'Kayıt sırasında bir hata oluştu. Lütfen bilgileri kontrol edin.')
    else:
        form = UserCreationForm()
    return render(request, 'hesap/kayit.html', {'form': form})

def giris(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Başarıyla giriş yaptınız!')
                return redirect('finans:anasayfa')
            else:
                messages.error(request, 'Kullanıcı adı veya şifre yanlış.')
        else:
            messages.error(request, 'Giriş sırasında bir hata oluştu.')
    else:
        form = AuthenticationForm()
    return render(request, 'hesap/giris.html', {'form': form})

@login_required
def cikis(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız!')
    return redirect('hesap:giris')