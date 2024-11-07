from django.urls import path
from . import views
from .views import PreferenciasViagemView
from .views import password_reset
from django.conf.urls.static import static


urlpatterns = [

    path('', views.home, name='home'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path("preferencias/<int:usuario_id>/", PreferenciasViagemView.as_view(), name="preferencias_user"),
    path('login/', views.login, name='login'),
    path('recomendacoes/', views.listar_recomendacoes, name='listar_recomendacoes'),
    path('redefinir-senha/', password_reset, name='password_reset'),
    #path('weather/', views.weather_view, name='weather'),
    
]
