from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as login_usuario, logout as logout_usuario
from .models import Usuario, PontoTuristico
from .forms import FormularioCadastroUsuario, PasswordResetForm
from django.views import View
from django.contrib.auth.hashers import make_password
import requests
from django.conf import settings
import unidecode

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
        interesses = request.POST.getlist('interesses')
        gastronomia = request.POST.getlist('gastronomia')
        estilo = request.POST.getlist('estilo')

        usuario.interesses = ','.join(interesses) if interesses else ''
        usuario.gastronomia = ','.join(gastronomia) if gastronomia else ''
        usuario.estilo = ','.join(estilo) if estilo else ''
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
                return redirect('listar_recomendacoes')
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
    logout_usuario(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('login')

def listar_recomendacoes(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    cidade = request.GET.get('cidade', '')
    pontos_turisticos = PontoTuristico.objects.filter(cidade=cidade)

    if usuario.interesses:
        interesses = usuario.interesses.split(',')
        for interesse in interesses:
            interesse = interesse.strip()
            if interesse == 'Praia':
                pontos_turisticos = pontos_turisticos.filter(interesse_praia=True)
            elif interesse == 'Natureza':
                pontos_turisticos = pontos_turisticos.filter(interesse_natureza=True)
            elif interesse == 'Cultura Local':
                pontos_turisticos = pontos_turisticos.filter(interesse_cultura_local=True)
            elif interesse == 'Aventura':
                pontos_turisticos = pontos_turisticos.filter(interesse_aventura=True)
            elif interesse == 'Compras':
                pontos_turisticos = pontos_turisticos.filter(interesse_compras=True)

    if usuario.gastronomia:
        gastronomia = usuario.gastronomia.split(',')
        for tipo in gastronomia:
            tipo = tipo.strip()
            if tipo == 'Culinária Oriental':
                pontos_turisticos = pontos_turisticos.filter(culinaria_oriental=True)
            elif tipo == 'Vegetariano':
                pontos_turisticos = pontos_turisticos.filter(vegetariano=True)
            elif tipo == 'Churrasco':
                pontos_turisticos = pontos_turisticos.filter(churrasco=True)
            elif tipo == 'Vegano':
                pontos_turisticos = pontos_turisticos.filter(vegano=True)
            elif tipo == 'Frutos do Mar':
                pontos_turisticos = pontos_turisticos.filter(frutos_do_mar=True)

    if usuario.estilo:
        estilos = usuario.estilo.split(',')
        for estilo in estilos:
            estilo = estilo.strip()
            if estilo == 'Relaxante':
                pontos_turisticos = pontos_turisticos.filter(estilo_relaxante=True)
            elif estilo == 'Cultural':
                pontos_turisticos = pontos_turisticos.filter(estilo_cultural=True)
            elif estilo == 'Família':
                pontos_turisticos = pontos_turisticos.filter(estilo_familia=True)
            elif estilo == 'Luxuoso':
                pontos_turisticos = pontos_turisticos.filter(estilo_luxuoso=True)
            elif estilo == 'Gastronômico':
                pontos_turisticos = pontos_turisticos.filter(estilo_gastronomico=True)

    weather_translations = {
        "clear sky": "céu limpo",
        "few clouds": "poucas nuvens",
        "scattered clouds": "levemente nublado",
        "broken clouds": "parcialmente nublado",
        "overcast clouds": "nublado",
        "light rain": "chuva fraca",
        "moderate rain": "chuva moderada",
        "heavy intensity rain": "chuva forte",
        "light snow": "neve leve",
        "moderate snow": "neve moderada",
        "heavy snow": "neve pesada",
        "fog": "neblina",
        "mist": "névoa",
        "haze": "nevoeiro",
        "dust": "poeira",
        "sand": "areia",
        "ash": "cinzas",
        "squall": "rajada de vento",
        "tornado": "tornado",
    }

    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric"
    response = requests.get(url)

    clima = {}
    if response.status_code == 200:
        data = response.json()
        condition = data['weather'][0]['description']
        translated_condition = weather_translations.get(condition, condition)

        clima = {
            'temperatura': data['main']['temp'],
            'condicao': translated_condition,
            'umidade': data['main']['humidity'],
            'vento': data['wind']['speed']
        }

    return render(request, 'usuarios/recomendacoes.html', {
        'pontos': pontos_turisticos,
        'cidade': cidade,
        'clima': clima
    })
