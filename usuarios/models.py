from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15)
    senha = models.CharField(max_length=128)
    genero = models.CharField(
        max_length=10, 
        choices=[
            ('M', 'Masculino'), 
            ('F', 'Feminino'), 
            ('P', 'Prefiro não dizer'), 
            ('O', 'Outros'),
        ]
    )

    
    INTERESSES_CHOICES = [
        ('Praia', 'Praia'),
        ('Cachoeira', 'Cachoeira'),
        ('Natureza', 'Natureza'),
        ('Cultura Local', 'Cultura Local'),
        ('Trilha', 'Trilha'),
        ('Passeios em Família', 'Passeios em Família'),
    ]
    
    GASTRONOMIA_CHOICES = [
        ('Culinária Oriental', 'Culinária Oriental'),
        ('Vegetariano', 'Vegetariano'),
        ('Churrasco', 'Churrasco'),
        ('Vegano', 'Vegano'),
        ('Frutos do Mar', 'Frutos do Mar'),
    ]
    
    ESTILO_CHOICES = [
        ('Aventura', 'Aventura'),
        ('Relaxante', 'Relaxante'),
        ('Cultural', 'Cultural'),
        ('Família', 'Família'),
        ('Luxuoso', 'Luxuoso'),
    ]

    interesses = models.CharField(max_length=50, choices=INTERESSES_CHOICES, blank=True)
    gastronomia = models.CharField(max_length=50, choices=GASTRONOMIA_CHOICES, blank=True)
    estilo = models.CharField(max_length=50, choices=ESTILO_CHOICES, blank=True)

    def save(self, *args, **kwargs): 
        if self.pk is None: 
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)

    def verificar_senha(self, senha_bruta):
        return check_password(senha_bruta, self.senha)

    def __str__(self):
        return self.email
