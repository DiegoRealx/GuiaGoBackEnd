from django.urls import path
from . import views
from .views import PreferenciasViagemView

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('preferencias/<int:usuario_id>/', PreferenciasViagemView.as_view(), name='preferencias_user'),
    path('login/', views.login, name='login'),
    path('recomendacoes/<int:usuario_id>/', views.listar_recomendacoes, name='listar_recomendacoes'),
    path('logout/', views.logout, name='logout'),
    path('redefinir-senha/', views.password_reset, name='password_reset'),
]
