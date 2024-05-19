from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager

from slugify import slugify

from frontend.signals import filling_user_training_model


class ManualUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class ManualUser(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[AbstractUser.username_validator],
        blank=True,
        null=True
    )
    email = models.EmailField(_("email address"), unique=True)

    is_active = models.BooleanField(
        _('active'),
        default=False
    )

    objects = ManualUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


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
