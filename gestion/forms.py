from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Conducteur, Moto, AgentControle


class GestionnaireCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ConducteurForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        fields = '__all__'

        exclude = ['qr_code', 'gestionnaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'prenoms': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'date_naissance': forms.DateInput(attrs={
                'type': 'date', 'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'
            }),
            'numero_identification': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'numero_assurance': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'type_assurance': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),

            # ✅ Nouveau champ : date de souscription à l’assurance
            'date_souscription_assurance': forms.DateInput(attrs={
                'type': 'date', 'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'
            }),

            # ✅ Nouveau champ : validité de l’assurance (date)
            'validite_assurance': forms.DateInput(attrs={
                'type': 'date', 'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'
            }),

            'numero_droit_taxi': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),

            # ✅ Nouveau champ : date de souscription au droit taxi
            'date_souscription_droit_taxi': forms.DateInput(attrs={
                'type': 'date', 'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'
            }),

            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow', 'rows': 2
            }),
            'telephone': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'photo': forms.ClearableFileInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
        }


class MotoForm(forms.ModelForm):
    class Meta:
        model = Moto
        exclude = ['conducteur']  # on associe la moto au conducteur dans la vue
        widgets = {
            'marque': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'modele': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'annee_fabrication': forms.NumberInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'immatriculation': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'couleur': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
            'numero_chassis': forms.TextInput(
                attrs={'class': 'w-full px-3 py-2 border rounded bg-white text-gray-900 shadow'}),
        }


class AgentControleForm(forms.ModelForm):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=False)

    class Meta:
        model = AgentControle
        fields = []  # Tu gères les champs manuellement

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        # Pré-remplir les champs si on modifie un agent existant
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if self.instance and self.instance.user:
            # Mise à jour utilisateur existant
            user = self.instance.user
            user.username = username
            if password:
                user.set_password(password)
            if commit:
                user.save()
        else:
            # Création utilisateur
            user = User.objects.create_user(
                username=username,
                password=password or User.objects.make_random_password()
            )

        agent = super().save(commit=False)
        agent.user = user
        if commit:
            agent.save()
        return agent

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.user_instance:
            qs = qs.exclude(pk=self.user_instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username