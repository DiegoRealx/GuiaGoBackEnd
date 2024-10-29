from django.db import models

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

