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
        ('Natureza', 'Natureza'),
        ('Cultura Local', 'Cultura Local'),
        ('Aventura', 'Aventura'),
        ('Compras', 'Compras'),
    ]

    GASTRONOMIA_CHOICES = [
        ('Culinária Oriental', 'Culinária Oriental'),
        ('Vegetariano', 'Vegetariano'),
        ('Churrasco', 'Churrasco'),
        ('Vegano', 'Vegano'),
        ('Frutos do Mar', 'Frutos do Mar'),
    ]

    ESTILO_CHOICES = [
        ('Relaxante', 'Relaxante'),
        ('Cultural', 'Cultural'),
        ('Família', 'Família'),
        ('Luxuoso', 'Luxuoso'),
        ('Gastronômico', 'Gastronômico'),
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


class PontoTuristico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    localizacao = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='imagens_pontos_turisticos/', blank=True, null=True)

    interesse_praia = models.BooleanField(default=False)
    interesse_natureza = models.BooleanField(default=False)
    interesse_cultura_local = models.BooleanField(default=False)
    interesse_aventura = models.BooleanField(default=False)
    interesse_compras = models.BooleanField(default=False)

    culinaria_oriental = models.BooleanField(default=False)
    vegetariano = models.BooleanField(default=False)
    churrasco = models.BooleanField(default=False)
    vegano = models.BooleanField(default=False)
    frutos_do_mar = models.BooleanField(default=False)

    estilo_relaxante = models.BooleanField(default=False)
    estilo_cultural = models.BooleanField(default=False)
    estilo_familia = models.BooleanField(default=False)
    estilo_luxuoso = models.BooleanField(default=False)
    estilo_gastronomico = models.BooleanField(default=False)

    popularidade = models.IntegerField(help_text="Popularidade de 1 a 10")

    def __str__(self):
        return self.nome
