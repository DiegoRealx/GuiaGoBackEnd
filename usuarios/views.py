from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as login_usuario, logout as logout_usuario
from .models import Usuario
from .forms import FormularioCadastroUsuario

def cadastrar(request):
    if request.method == 'POST':
        formulario = FormularioCadastroUsuario(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('login')  
    else:
        formulario = FormularioCadastroUsuario()
    return render(request, 'usuarios/cadastrar.html', {'formulario': formulario})

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['password']
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.verificar_senha(senha):  
                request.session['usuario_id'] = usuario.id
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('listar_usuarios')  
            else:
                messages.error(request, 'Senha incorreta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
    return render(request, 'usuarios/login.html')

def logout(request):
    logout_usuario(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('login')

def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

def solicitar_redefinicao_senha(request):
    return render(request, 'usuarios/solicitar_redefinicao_senha.html')