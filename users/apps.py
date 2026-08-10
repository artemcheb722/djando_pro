from django.apps import AppConfig
from django.db.models.signals import post_save
from integrations.signals import on_user_saved

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        post_save.connect(on_user_saved, sender=self.get_model("User"))