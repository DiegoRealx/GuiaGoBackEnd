from django import forms
from .models import Usuario

class FormularioCadastroUsuario(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    confirma_senha = forms.CharField(label="Confirme sua senha", widget=forms.PasswordInput)
    
    class Meta:
        model = Usuario
        fields = ['email', 'nome_completo', 'telefone', 'senha', 'genero']
