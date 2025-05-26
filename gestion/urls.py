from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import conducteur_create, agent_create, conducteur_detail, dashboard, conducteur_api, ajouter_gestionnaire

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
path('conducteurs/', views.liste_conducteurs, name='liste_conducteurs'),
    path('conducteur/ajouter/', conducteur_create, name='conducteur_create'),
    path('agent/ajouter/', agent_create, name='agent_create'),
    path('conducteur/<int:pk>/', conducteur_detail, name='conducteur_detail'),
    path('conducteur/modifier/<int:pk>/', views.modifier_conducteur, name='modifier_conducteur'),
    path('conducteur/supprimer/<int:pk>/', views.supprimer_conducteur, name='supprimer_conducteur'),
    path('api/conducteur/<int:pk>/', conducteur_api, name='conducteur_api'),
    path('admin/ajouter-gestionnaire/', ajouter_gestionnaire, name='ajouter_gestionnaire'),
    path('accounts/login/', auth_views.LoginView.as_view(
        redirect_authenticated_user=True,
        template_name='registration/login.html'), name='login'),
    path('conducteurs/<int:pk>/print/', views.print_qr_conducteur, name='print_qr_conducteur'),
    path('public/conducteur/<int:pk>/', views.conducteur_detail, name='conducteur_public'),

    path('agent/conducteur/<int:pk>/', views.agent_conducteur_detail, name='agent_conducteur_detail'),
    path('agent/modifier/<int:pk>/', views.modifier_agent, name='modifier_agent'),
    path('agent/supprimer/<int:pk>/', views.supprimer_agent, name='supprimer_agent'),
    path('moto/modifier/<int:pk>/', views.modifier_moto, name='modifier_moto'),
    path('moto/supprimer/<int:pk>/', views.supprimer_moto, name='supprimer_moto'),
    path('logout/', views.custom_logout, name='logout'),

]

