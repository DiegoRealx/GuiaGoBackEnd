from django.contrib import admin
from .models import Usuario
from .models import PontoTuristico

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome_completo', 'telefone', 'genero')
    search_fields = ('email', 'nome_completo')



class PontoTuristicoAdmin(admin.ModelAdmin):
    # Exibir campos na lista
    list_display = ('nome', 'cidade', 'popularidade')
    
    # Permitir busca por campos específicos
    search_fields = ('nome', 'cidade')
    
    # Filtros laterais para facilitar a navegação
    list_filter = ('cidade', 'interesse_praia', 'interesse_natureza', 'interesse_cultura_local',
                   'culinaria_oriental', 'vegetariano', 'churrasco', 'vegano', 'frutos_do_mar',
                   'estilo_relaxante', 'estilo_cultural', 'estilo_familia', 'estilo_luxuoso', 
                   'estilo_gastronomico')
    
    # Opções de edição em massa
    list_editable = ('popularidade',)

# Registrar a classe no admin
admin.site.register(PontoTuristico, PontoTuristicoAdmin)

