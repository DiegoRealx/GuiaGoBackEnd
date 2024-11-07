from django.contrib import admin
from .models import Usuario
from .models import PontoTuristico

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome_completo', 'telefone', 'genero')
    search_fields = ('email', 'nome_completo')



class PontoTuristicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'popularidade')
    
    search_fields = ('nome', 'cidade')
    
    list_filter = ('cidade', 'interesse_praia', 'interesse_natureza', 'interesse_cultura_local',
                   'culinaria_oriental', 'vegetariano', 'churrasco', 'vegano', 'frutos_do_mar',
                   'estilo_relaxante', 'estilo_cultural', 'estilo_familia', 'estilo_luxuoso', 
                   'estilo_gastronomico')
    
    list_editable = ('popularidade',)

admin.site.register(PontoTuristico, PontoTuristicoAdmin)

