from django.db.models.signals import post_save, pre_save, pre_init
from django.dispatch import receiver


from statements.models import Statement


# @receiver(post_save, sender=Statement)
# def save_user_profile(sender, instance, **kwargs):

#     print('=================')
#     print(f'Number of class instance is: {instance.number}')
#     print('=================')


#     print('=================')
#     print(f'Number of class instance is: {sender}')
#     print('=================')




@receiver(pre_save, sender=Statement)
def save_user_profile(sender, instance, **kwargs):

    if not instance._state.adding:
        print ('this is an update')
    else:
        print ('this is an insert')