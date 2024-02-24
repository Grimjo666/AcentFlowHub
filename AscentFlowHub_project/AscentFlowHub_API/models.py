from django.db import models
from django.contrib.auth.models import User

from transliterate import translit


class ProgressCircleModel(models.Model):
    name = models.CharField(max_length=25, null=False)
    latin_name = models.CharField(max_length=25, default='', blank=True)
    percent = models.IntegerField(default=0)
    first_color = models.CharField(max_length=20, blank=True)
    second_color = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def custom_translit(text):
        try:
            # Если текст является кириллическим
            result = translit(text, 'ru', reversed=True)
        except Exception:
            # Если текст не является кириллическим
            result = text
        return result

    def save(self, *args, **kwargs):
        self.latin_name = self.custom_translit(self.name)
        super(LifeSphereModel, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} {self.percent}'
