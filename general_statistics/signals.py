from django.db.models.signals import post_save
from django.dispatch import receiver


from statements.models import Statement


@receiver(post_save, sender=Statement)
def save_user_profile(sender, instance, **kwargs):
    print('You have saved statemtn! CNGS!')