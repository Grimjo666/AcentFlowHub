from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='api.ManualUser')
def filling_user_training_model(sender, instance, created, **kwargs):
    if created:
        from .models import UserTraining
        # Создаём экземпляр модели обучения пользователя
        user_training = UserTraining(user=instance).save()


# @receiver(request_finished)
# def writing_user_training_data_to_session(sender, **kwargs):
#     print(kwargs)
#     print(sender)
