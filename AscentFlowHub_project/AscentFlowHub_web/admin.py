from django.contrib import admin

from AscentFlowHub_API import models
from AscentFlowHub_web.models import UserTrainingModel

admin.site.register(models.LifeCategoryModel)
admin.site.register(UserTrainingModel)
admin.site.register(models.TreeGoalsModel)