
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .decorators import agent_required
from .models import Conducteur, Moto, AgentControle, Gestionnaire
from .serializers import ConducteurSerializer
from .forms import ConducteurForm, MotoForm, AgentControleForm, UserForm


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from .models import Conducteur, AgentControle, Gestionnaire
from .forms import GestionnaireCreationForm

@login_required
def dashboard(request):
    query = request.GET.get('q', '')
    filtre = request.GET.get('filtre', '')
    try:
        gestionnaire = request.user.gestionnaire
    except Gestionnaire.DoesNotExist:
        return redirect('home')

    agents = AgentControle.objects.all()
    conducteurs = Conducteur.objects.all()
    motos = Moto.objects.all()

    if not filtre or filtre == 'conducteurs':
        conducteurs = Conducteur.objects.filter(nom__icontains=query)
    if not filtre or filtre == 'agents':
        agents = AgentControle.objects.filter(user__username__icontains=query)
    if not filtre or filtre == 'motos':
        motos = Moto.objects.filter(immatriculation__icontains=query)

    context = {
        'gestionnaire': gestionnaire,
        'conducteurs': conducteurs,
        'agents': agents,
        'motos': motos,
    }
    return render(request, 'gestion/dashboard.html', context)

@login_required
def liste_conducteurs(request):
    conducteurs = Conducteur.objects.all()
    return render(request, 'gestion/liste_conducteurs.html', {'conducteurs': conducteurs})





def conducteur_detail(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    return render(request, 'gestion/conducteur_detail.html', {'conducteur': conducteur})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conducteur_api(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    serializer = ConducteurSerializer(conducteur)
    return Response(serializer.data)


@login_required
def conducteur_create(request):
    if not hasattr(request.user, 'gestionnaire'):
        messages.error(request, "Accès refusé : Vous devez être un gestionnaire pour créer un conducteur.")
        return redirect('dashboard')

    if request.method == 'POST':
        conducteur_form = ConducteurForm(request.POST, request.FILES)
        moto_form = MotoForm(request.POST)

        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            if photo.size > 5 * 1024 * 1024:
                messages.error(request, "Le fichier est trop volumineux (taille maximale : 5 Mo).")
                return render(request, 'gestion/conducteur_form.html', {
                    'conducteur_form': conducteur_form,
                    'moto_form': moto_form
                })
            if not photo.content_type.startswith('image/'):
                messages.error(request, "Le fichier doit être une image.")
                return render(request, 'gestion/conducteur_form.html', {
                    'conducteur_form': conducteur_form,
                    'moto_form': moto_form
                })

        if conducteur_form.is_valid() and moto_form.is_valid():
            try:
                conducteur = conducteur_form.save(commit=False)
                conducteur.save()
                conducteur.generate_qr_code()
                conducteur.save()

                moto = moto_form.save(commit=False)
                moto.conducteur = conducteur
                moto.save()

                messages.success(request, "Conducteur et moto ajoutés avec succès.")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {e}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        conducteur_form = ConducteurForm()
        moto_form = MotoForm()

    return render(request, 'gestion/conducteur_form.html', {
        'conducteur_form': conducteur_form,
        'moto_form': moto_form
    })


@login_required
def modifier_conducteur(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    if request.method == 'POST':
        form = ConducteurForm(request.POST, request.FILES, instance=conducteur)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ConducteurForm(instance=conducteur)
    return render(request, 'gestion/modifier_conducteur.html', {'form': form})


@login_required
def supprimer_conducteur(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    if request.method == 'POST':
        conducteur.delete()
        return redirect('dashboard')
    return render(request, 'gestion/confirmation_suppression_conducteur.html', {'conducteur': conducteur})


@login_required
def agent_create(request):
    if not hasattr(request.user, 'gestionnaire'):
        messages.error(request, "Accès refusé : Vous devez être un gestionnaire pour créer un agent.")
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not email or not password:
            messages.error(request, "Tous les champs sont requis.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            try:
                # Créer le compte utilisateur
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                )

                # Lier à un agent de contrôle
                AgentControle.objects.create(user=user)
                messages.success(request, "Agent de contrôle créé avec succès.")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Erreur : {e}")
    return render(request, 'gestion/agent_form.html')
@login_required
def modifier_agent(request, pk):
    agent = get_object_or_404(AgentControle, pk=pk)
    user = agent.user

    if request.method == 'POST':
        agent_form = AgentControleForm(request.POST, instance=agent)
        user_form = UserForm(request.POST, instance=user)

        if agent_form.is_valid() and user_form.is_valid():
            user_form.save()
            agent_form.save()
            messages.success(request, "L'agent a été mis à jour avec succès.")
            return redirect('dashboard')
    else:
        agent_form = AgentControleForm(instance=agent)
        user_form = UserForm(instance=user)

    return render(request, 'gestion/modifier_agent.html', {
        'agent_form': agent_form,
        'user_form': user_form,
    })

@login_required
def supprimer_agent(request, pk):
    agent = get_object_or_404(AgentControle, pk=pk)
    if request.method == 'POST':
        agent.delete()
        return redirect('dashboard')
    return render(request, 'gestion/confirmation_suppression_agent.html', {'agent': agent})


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def ajouter_gestionnaire(request):
    if request.method == 'POST':
        form = GestionnaireCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # ou False si tu veux l'activer plus tard
            user.save()

            # Ajouter au groupe "Gestionnaire"
            try:
                gestionnaire_group = Group.objects.get(name="Gestionnaire")
                user.groups.add(gestionnaire_group)
            except Group.DoesNotExist:
                messages.warning(request, "Groupe 'Gestionnaire' introuvable.")

            messages.success(request, "Gestionnaire ajouté avec succès.")
            return redirect('dashboard')
        else:
            messages.error(request, "Erreur lors de l'ajout du gestionnaire.")
    else:
        form = GestionnaireCreationForm()

    return render(request, 'gestion/ajouter_gestionnaire.html', {'form': form})


def home(request):
    return render(request, 'gestion/home.html')


def custom_login(request):
    next_url = request.GET.get('next', '')  # 🔁 récupère la redirection demandée

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')  # 🔁 récupère la redirection dans POST

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if hasattr(user, 'gestionnaire'):
                return redirect('dashboard')
            elif hasattr(user, 'agentcontrole'):
                return redirect(next_url or 'agent_dashboard')  # ✅ redirection prioritaire
            else:
                messages.error(request, "Ce compte n'a pas de rôle associé.")
                return redirect('custom_login')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")

    return render(request, 'registration/login.html', {'next': next_url})

@login_required
def print_qr_conducteur(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    return render(request, 'gestion/print_qr.html', {'conducteur': conducteur})

def public_conducteur_detail(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    return render(request, 'gestion/conducteur_detail.html', {'conducteur': conducteur})

class AgentLoginView(LoginView):
    template_name = 'gestion /login.html'


@login_required
def agent_conducteur_detail(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    return render(request, 'agent/conducteur_detail.html', {'conducteur': conducteur})


@agent_required
def conducteur_agent_detail(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)

    # Vérifie si l'utilisateur connecté est un agent
    if not hasattr(request.user, 'agentcontrole'):
        return redirect('custom_login')

    return render(request, 'agent/conducteur_detail.html', {'conducteur': conducteur})

def custom_logout(request):
    logout(request)
    messages.success(request, "Déconnexion réussie.")
    return redirect('login')
@login_required
def modifier_moto(request, pk):
    moto = get_object_or_404(Moto, pk=pk)

    if request.method == 'POST':
        form = MotoForm(request.POST, instance=moto)
        if form.is_valid():
            form.save()
            messages.success(request, "Moto modifiée avec succès.")
            return redirect('dashboard')
    else:
        form = MotoForm(instance=moto)

    return render(request, 'gestion/modifier_moto.html', {'form': form})

@login_required
def supprimer_moto(request, pk):
    moto = get_object_or_404(Moto, pk=pk)

    if request.method == 'POST':
        moto.delete()
        messages.success(request, "Moto supprimée avec succès.")
        return redirect('dashboard')

    return render(request, 'gestion/confirmation_suppression_moto.html', {'moto': moto})

@login_required
def agent_dashboard(request):
    return render(request, 'agent/agent_dashboard.html')




