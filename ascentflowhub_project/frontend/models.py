from django.db import models
from django.contrib.auth.models import User


class UserTraining(models.Model):
    """
    Модель для обучения пользователя элементам на сайте
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    creating_base_categories = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} /  creating base categories: {self.creating_base_categories}'


class UserSettings(models.Model):
    """
    Модель для настроек сайта аккаунта пользователя
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hide_subgoals = models.BooleanField(default=False)


class UserProfilePhoto(models.Model):
    photo = models.FileField(upload_to='user_profile_photos')
    main_photo = models.BooleanField(default=False)
    load_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)