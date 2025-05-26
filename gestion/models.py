from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse

class Gestionnaire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gestionnaire: {self.user.username}"
# Create your models here.
class Conducteur(models.Model):
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    date_naissance = models.DateField()
    numero_identification = models.CharField(max_length=50, unique=True)
    numero_assurance = models.CharField(max_length=50)
    type_assurance = models.CharField(max_length=50)
    date_souscription_assurance = models.DateField(null=True, blank=True)  # ✅ ajouté
    validite_assurance = models.DateField(null=True, blank=True)           # ✅ ajouté
    numero_droit_taxi = models.CharField(max_length=50)
    date_souscription_droit_taxi = models.DateField(null=True, blank=True) # ✅ ajouté
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='photos_conducteurs/')
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenoms}"

    def get_absolute_url(self):
        return reverse('conducteur_detail', args=[str(self.pk)])

    def generate_qr_code(self):


        # Lien vers la page publique
        public_url = f"{settings.SITE_URL}/public/conducteur/{self.pk}/"

        # Génération QR
        qr = qrcode.make(public_url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        # Enregistrement
        file_name = f"{self.nom}_{self.prenoms}_qr.png"
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save(update_fields=["qr_code"])

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  # L'objet aura un ID ici
        if is_new and not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=["qr_code"])

class Moto(models.Model):
    conducteur = models.OneToOneField(Conducteur, on_delete=models.CASCADE)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    annee_fabrication = models.IntegerField()
    immatriculation = models.CharField(max_length=50, unique=True)
    couleur = models.CharField(max_length=50)
    numero_chassis = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.marque} {self.modele} - {self.immatriculation}"

class AgentControle(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username



