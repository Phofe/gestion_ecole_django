# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, User

from gestion.models import Gestionnaire


@receiver(post_save, sender=User)
def assign_gestionnaire_group(sender, instance, created, **kwargs):
    if created and instance.is_superuser:  # Adaptez cette condition selon vos besoins
        groupe_gestionnaire, _ = Group.objects.get_or_create(name='Gestionnaire')
        instance.groups.add(groupe_gestionnaire)
        Gestionnaire.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_gestionnaire_profile(sender, instance, created, **kwargs):
    if created and instance.groups.filter(name='Gestionnaire').exists():
        Gestionnaire.objects.get_or_create(user=instance)