from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome_completo', 'telefone', 'genero')
    search_fields = ('email', 'nome_completo')
