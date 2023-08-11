from django.apps import AppConfig
from django.db.models.signals import post_migrate, pre_save
from allauth.account.signals import user_signed_up


class TransferguideappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transferguideapp'

    def ready(self):
        from .signals import populate_models, hook_save, hook_signup
        post_migrate.connect(populate_models, sender=self)
        pre_save.connect(hook_save )
        user_signed_up.connect(hook_signup)
