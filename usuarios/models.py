from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15)
    senha = models.CharField(max_length=128)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outros')])

    def save(self, *args, **kwargs): # essa parte do codigo faz a criptografia da senha
        self.senha = make_password(self.senha)
        super().save(*args, **kwargs)

    def verificar_senha(self, senha_bruta):
        return check_password(senha_bruta, self.senha)

    def __str__(self):
        return self.email
