from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuario

class FormularioCadastroUsuario(forms.ModelForm):
    senha = forms.CharField(
    widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'}))
    
    confirma_senha = forms.CharField(
    label="Confirme sua senha", 
    widget=forms.PasswordInput(attrs={'placeholder': 'Confirme a sua senha'}))
    
    email = forms.EmailField(
    label ="Email",
     widget=forms.EmailInput(attrs={'placeholder': 'Digite seu email'})
    )
    nome_completo = forms.CharField(
    label ="Nome Completo",
     widget=forms.TextInput(attrs={'placeholder': 'Digite seu nome completo'})
    )
    telefone = forms.CharField(
    label ="Celular",
     widget=forms.TextInput(attrs={'placeholder': '(xx) xxxxx-xxxx'})
    )
     
    class Meta:
        model = Usuario
        fields = ['email', 'nome_completo', 'telefone', 'senha', 'genero', 'interesses', 'gastronomia', 'estilo']
      
  
    def clean_email(self):
        email=self.cleaned_data.get("email")
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail ja esta cadastrado.")
        return email
    
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

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    new_password = forms.CharField(label="Nova senha", widget=forms.PasswordInput)
