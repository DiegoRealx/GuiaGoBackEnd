from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as login_usuario, logout as logout_usuario
from .models import Usuario
from .forms import FormularioCadastroUsuario, PasswordResetForm
from django.views import View
from django.contrib.auth.hashers import make_password

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
                return redirect('listar_usuarios')
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

def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})
