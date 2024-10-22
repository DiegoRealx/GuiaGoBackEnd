from django.urls import path
from . import views
from .views import PreferenciasViagemView

urlpatterns = [

    path('', views.home, name='home'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path("preferencias/<int:usuario_id>/", PreferenciasViagemView.as_view(), name="preferencias_user"),
    path('login/', views.login, name='login'),
    path('listar/', views.listar_usuarios, name='listar_usuarios'),
]
