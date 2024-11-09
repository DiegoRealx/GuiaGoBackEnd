from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as login_usuario, logout as logout_usuario
from django.views import View
from django.conf import settings
from django.contrib.auth.hashers import make_password
import numpy as np
from sklearn.neighbors import NearestNeighbors
import requests
from .models import Usuario, PontoTuristico
from .forms import FormularioCadastroUsuario, PasswordResetForm
from .decorators import login_required_custom


# Página inicial
def home(request):
    return render(request, 'usuarios/home.html')


# Cadastro de usuário
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


# Preferências de viagem do usuário
class PreferenciasViagemView(View):
    template_name = 'usuarios/preferencias.html'

    def get(self, request, usuario_id):
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, self.template_name, {
            'usuario': usuario,
            'interesses_selecionados': usuario.interesses.split(',') if usuario.interesses else [],
            'gastronomia_selecionada': usuario.gastronomia.split(',') if usuario.gastronomia else [],
            'estilo_selecionado': usuario.estilo.split(',') if usuario.estilo else [],
        })

    def post(self, request, usuario_id):
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.interesses = ','.join(request.POST.getlist('interesses')) if 'interesses' in request.POST else ''
        usuario.gastronomia = ','.join(request.POST.getlist('gastronomia')) if 'gastronomia' in request.POST else ''
        usuario.estilo = ','.join(request.POST.getlist('estilo')) if 'estilo' in request.POST else ''
        usuario.save()
        return redirect('login')


# Login de usuário
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['password']
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.verificar_senha(senha):
                request.session['usuario_id'] = usuario.id
                next_url = request.GET.get('next')
                return redirect(next_url) if next_url else redirect('listar_recomendacoes', usuario_id=usuario.id)
            else:
                messages.error(request, 'Senha incorreta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
    return render(request, 'usuarios/login.html')


# Redefinição de senha
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


# Logout de usuário
def logout(request):
    request.session.pop('usuario_id', None)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('login')


# Tradução das condições climáticas
weather_translations = {
    "clear sky": "céu limpo", "few clouds": "poucas nuvens", "scattered clouds": "levemente nublado",
    "broken clouds": "parcialmente nublado", "overcast clouds": "nublado", "light rain": "chuva fraca",
    "moderate rain": "chuva moderada", "heavy intensity rain": "chuva forte", "light snow": "neve leve",
    "moderate snow": "neve moderada", "heavy snow": "neve pesada", "fog": "neblina", "mist": "névoa",
    "haze": "nevoeiro", "dust": "poeira", "sand": "areia", "ash": "cinzas", "squall": "rajada de vento",
    "tornado": "tornado"
}


# Preparação de dados para recomendação com a IA
def preparar_dados_para_ia(pontos_turisticos, atributos):
    return np.array([[getattr(ponto, attr) for attr in atributos] for ponto in pontos_turisticos])


# Listar recomendações de locais 
@login_required_custom
def listar_recomendacoes(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    cidade = request.GET.get('cidade', '').strip()
    pontos_turisticos = PontoTuristico.objects.filter(cidade__iexact=cidade)

    if not pontos_turisticos.exists():
        return render(request, 'usuarios/recomendacoes.html', {
            'usuario_id': usuario_id,
            'usuario': usuario,
            'recomendacoes': {},
            'cidade': cidade,
            'clima': {},
            'mensagem': f"Não foram encontrados pontos turísticos para a cidade {cidade}."
        })

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

    def obter_recomendacao_por_preferencia(preferencia, mapa):
        campo = mapa.get(preferencia.strip())
        if not campo:
            return None

        perfil_usuario = [0] * len(mapa)
        perfil_usuario[list(mapa.values()).index(campo)] = 1

        dados_pontos = preparar_dados_para_ia(pontos_turisticos, list(mapa.values()))
        ids_pontos = [ponto.id for ponto in pontos_turisticos]

        if dados_pontos.size == 0:
            return None

        knn = NearestNeighbors(n_neighbors=1, metric='cosine')
        knn.fit(dados_pontos)
        perfil_usuario = np.array(perfil_usuario).reshape(1, -1)
        _, indices = knn.kneighbors(perfil_usuario)
        
        return pontos_turisticos.filter(id=ids_pontos[indices[0][0]]).first()

    recomendacoes = {
        'interesse': [obter_recomendacao_por_preferencia(i, interesse_map) for i in (usuario.interesses or '').split(',') if obter_recomendacao_por_preferencia(i, interesse_map)],
        'gastronomia': [obter_recomendacao_por_preferencia(g, gastronomia_map) for g in (usuario.gastronomia or '').split(',') if obter_recomendacao_por_preferencia(g, gastronomia_map)],
        'estilo': [obter_recomendacao_por_preferencia(e, estilo_map) for e in (usuario.estilo or '').split(',') if obter_recomendacao_por_preferencia(e, estilo_map)]
    }

    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric"
    response = requests.get(url)
    clima = {}
    if response.status_code == 200:
        data = response.json()
        condicao = weather_translations.get(data['weather'][0]['description'], data['weather'][0]['description'])
        clima = {
            'temperatura': data['main']['temp'],
            'condicao': condicao,
            'umidade': data['main']['humidity'],
            'vento': data['wind']['speed']
        }

    return render(request, 'usuarios/recomendacoes.html', {
        'usuario_id': usuario_id,
        'usuario': usuario,
        'recomendacoes': recomendacoes,
        'cidade': cidade,
        'clima': clima
    })
