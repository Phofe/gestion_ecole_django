from gestion.models import Gestionnaire  # ajuste si ton modèle est ailleurs

class DebugUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            print("🔐 Utilisateur authentifié")
            print(f"🧑 Groupes de l'utilisateur : {[group.name for group in request.user.groups.all()]}")
            try:
                if request.user.gestionnaire:
                    print("✅ L'utilisateur est un gestionnaire")
            except Gestionnaire.DoesNotExist:
                print("❌ L'utilisateur n'est pas un gestionnaire")
        else:
            print("🚫 Utilisateur non authentifié")

        return self.get_response(request)
