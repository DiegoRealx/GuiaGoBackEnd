from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as login_usuario, logout as logout_usuario
from django.views import View
from django.conf import settings
from django.contrib.auth.hashers import make_password
import requests
from .models import Usuario, PontoTuristico
from .forms import FormularioCadastroUsuario
from .forms import PasswordResetForm
from .decorators import login_required_custom

def home(request):
    return render(request, 'usuarios/home.html')

def cadastrar(request):
    if request.method == 'POST':
        formulario = FormularioCadastroUsuario(request.POST)
        if formulario.is_valid():
            usuario = formulario.save(commit=False)
            usuario.senha = formulario.cleaned_data['senha']
            usuario.save()
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('preferencias_user', usuario_id=usuario.id)
    else:
        formulario = FormularioCadastroUsuario()
    return render(request, 'usuarios/cadastrar.html', {'formulario': formulario})

class PreferenciasViagemView(View):
    template_name = 'usuarios/preferencias.html'

    def get(self, request, usuario_id):
        usuario = Usuario.objects.get(id=usuario_id)
        interesses_selecionados = usuario.interesses.split(',') if usuario.interesses else []
        gastronomia_selecionada = usuario.gastronomia.split(',') if usuario.gastronomia else []
        estilo_selecionado = usuario.estilo.split(',') if usuario.estilo else []
        return render(request, self.template_name, {
            'usuario': usuario,
            'interesses_selecionados': interesses_selecionados,
            'gastronomia_selecionada': gastronomia_selecionada,
            'estilo_selecionado': estilo_selecionado,
        })

    def post(self, request, usuario_id):
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.interesses = ','.join(request.POST.getlist('interesses')) if 'interesses' in request.POST else ''
        usuario.gastronomia = ','.join(request.POST.getlist('gastronomia')) if 'gastronomia' in request.POST else ''
        usuario.estilo = ','.join(request.POST.getlist('estilo')) if 'estilo' in request.POST else ''
        usuario.save()
        return redirect('login')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['password']
        
        try:
            usuario = Usuario.objects.get(email=email)
            
            if usuario.verificar_senha(senha):
                request.session['usuario_id'] = usuario.id
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('listar_recomendacoes', usuario_id=usuario.id)
            else:
                messages.error(request, 'Senha incorreta.')
        
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

    return render(request, 'usuarios/login.html')

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                messages.error(request, 'As senhas não correspondem.')
            else:
                try:
                    user = Usuario.objects.get(email=email)
                    user.senha = make_password(new_password)
                    user.save()
                    messages.success(request, 'Senha redefinida com sucesso.')
                    return redirect('login')
                except Usuario.DoesNotExist:
                    messages.error(request, 'Usuário com esse e-mail não encontrado.')
    else:
        form = PasswordResetForm()
    return render(request, 'usuarios/password_reset.html', {'form': form})

def logout(request):
    request.session.pop('usuario_id', None)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('login')

@login_required_custom
def listar_recomendacoes(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    cidade = request.GET.get('cidade', '')
    pontos_turisticos = PontoTuristico.objects.filter(cidade=cidade)
    interesse_map = {
        'Praia': 'interesse_praia', 'Natureza': 'interesse_natureza', 'Cultura Local': 'interesse_cultura_local',
        'Aventura': 'interesse_aventura', 'Compras': 'interesse_compras'
    }
    gastronomia_map = {
        'Culinária Oriental': 'culinaria_oriental', 'Vegetariano': 'vegetariano', 'Churrasco': 'churrasco',
        'Vegano': 'vegano', 'Frutos do Mar': 'frutos_do_mar'
    }
    estilo_map = {
        'Relaxante': 'estilo_relaxante', 'Cultural': 'estilo_cultural', 'Família': 'estilo_familia',
        'Luxuoso': 'estilo_luxuoso', 'Gastronômico': 'estilo_gastronomico'
    }

    for interesse in (usuario.interesses or '').split(','):
        campo = interesse_map.get(interesse.strip())
        if campo:
            pontos_turisticos = pontos_turisticos.filter(**{campo: True})
    for tipo in (usuario.gastronomia or '').split(','):
        campo = gastronomia_map.get(tipo.strip())
        if campo:
            pontos_turisticos = pontos_turisticos.filter(**{campo: True})
    for estilo in (usuario.estilo or '').split(','):
        campo = estilo_map.get(estilo.strip())
        if campo:
            pontos_turisticos = pontos_turisticos.filter(**{campo: True})

    weather_translations = {
        "clear sky": "céu limpo", "few clouds": "poucas nuvens", "scattered clouds": "levemente nublado",
        "broken clouds": "parcialmente nublado", "overcast clouds": "nublado", "light rain": "chuva fraca",
        "moderate rain": "chuva moderada", "heavy intensity rain": "chuva forte", "light snow": "neve leve",
        "moderate snow": "neve moderada", "heavy snow": "neve pesada", "fog": "neblina", "mist": "névoa",
        "haze": "nevoeiro", "dust": "poeira", "sand": "areia", "ash": "cinzas", "squall": "rajada de vento",
        "tornado": "tornado"
    }
    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric"
    response = requests.get(url)
    clima = {}
    if response.status_code == 200:
        data = response.json()
        translated_condition = weather_translations.get(data['weather'][0]['description'], data['weather'][0]['description'])
        clima = {
            'temperatura': data['main']['temp'],
            'condicao': translated_condition,
            'umidade': data['main']['humidity'],
            'vento': data['wind']['speed']
        }
    return render(request, 'usuarios/recomendacoes.html', {
        'usuario_id': usuario_id,
        'usuario': usuario,
        'pontos': pontos_turisticos,
        'cidade': cidade,
        'clima': clima
    })
