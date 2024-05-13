from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.apps import apps

from slugify import slugify

from frontend.signals import filling_user_training_model


class ManualUserManager(UserManager):
    def _create_user(self, email, password, username=None, **extra_fields):

        email = self.normalize_email(email)

        # GlobalUserModel = apps.get_model(
        #     self.model._meta.app_label, self.model._meta.object_name
        # )
        #
        # username = GlobalUserModel.normalize_username(username)
        user = self.model(email=email, username=username, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user


class ManualUser(AbstractUser):
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = ManualUserManager()


ManualUser.add_to_class('filling_user_training_model', filling_user_training_model)


class LifeCategory(models.Model):
    name = models.CharField(max_length=25, null=False)
    slug_name = models.SlugField(max_length=25, default='', blank=True)
    percent = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    first_color = models.CharField(max_length=20, blank=True)
    second_color = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(ManualUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} {self.percent}'


class TreeGoals(models.Model):
    WEIGHT_CHOICES = [
        (3, 'Высокое'),
        (2, 'Среднее'),
        (1, 'Низкое')
    ]

    name = models.CharField(max_length=45, null=False)
    slug_name = models.CharField(max_length=50, default='', blank=True)
    life_category = models.ManyToManyField(LifeCategory)
    weight = models.IntegerField(choices=WEIGHT_CHOICES, default=1)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    description = models.CharField(max_length=250, blank=True, null=True)
    user = models.ForeignKey(ManualUser, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        slug_name = slugify(self.name)

        if len(slug_name) > 40:
            self.slug_name = slug_name[0:39]
        else:
            self.slug_name = slug_name

        super(TreeGoals, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
