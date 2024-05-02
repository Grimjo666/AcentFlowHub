from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.signals import request_finished
from rest_framework.authtoken.models import Token

from .models import UserTraining


@receiver(post_save, sender=User)
def filling_user_training_model(sender, instance, created, **kwargs):
    if created:
        # Создаём экземпляр модели обучения пользователя
        user_training = UserTraining(user=instance).save()

# @receiver(request_finished)
# def writing_user_training_data_to_session(sender, **kwargs):
#     print(sender.session)
#
#
# request_finished.connect(writing_user_training_data_to_session)
