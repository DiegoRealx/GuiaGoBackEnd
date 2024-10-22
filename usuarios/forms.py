from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuario

class FormularioCadastroUsuario(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    confirma_senha = forms.CharField(label="Confirme sua senha", widget=forms.PasswordInput)
    
    class Meta:
        model = Usuario
        fields = ['email', 'nome_completo', 'telefone', 'senha', 'genero', 'interesses', 'gastronomia', 'estilo']

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirma_senha = cleaned_data.get("confirma_senha")

        if senha and confirma_senha and senha != confirma_senha:
            self.add_error('confirma_senha', "As senhas não coincidem.")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.senha = make_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario
