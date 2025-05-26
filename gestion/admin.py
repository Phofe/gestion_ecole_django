from django.contrib import admin

from gestion.models import Gestionnaire


if admin.site.is_registered(Gestionnaire):
    admin.site.unregister(Gestionnaire)

@admin.register(Gestionnaire)
class GestionnaireAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_creation')
# Register your models here.
