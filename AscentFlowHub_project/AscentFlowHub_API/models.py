from django.db import models
from django.contrib.auth.models import User

from slugify import slugify


class LifeCategoryModel(models.Model):
    name = models.CharField(max_length=25, null=False)
    slug_name = models.SlugField(max_length=25, default='', blank=True)
    percent = models.IntegerField(default=0)
    first_color = models.CharField(max_length=20, blank=True)
    second_color = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name)
        super(LifeCategoryModel, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} {self.percent}'


class TreeGoalsModel(models.Model):
    WEIGHT_CHOICES = [
        (1, 'Высокое'),
        (2, 'Среднее'),
        (3, 'Низкое')
    ]

    name = models.CharField(max_length=40, null=False)
    slug_name = models.CharField(max_length=40, default='', blank=True)
    life_category = models.ManyToManyField(LifeCategoryModel)
    weight = models.IntegerField(choices=WEIGHT_CHOICES, default=1)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    description = models.CharField(max_length=250, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        slug_name = slugify(self.name)

        if len(slug_name) > 40:
            self.slug_name = slug_name[0:39]
        else:
            self.slug_name = slug_name

        super(TreeGoalsModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
