from django.contrib import admin

from AscentFlowHub_API import models as api_models
from AscentFlowHub_web import models as web_models

admin.site.register(api_models.LifeCategoryModel)
admin.site.register(web_models.UserTrainingModel)
admin.site.register(api_models.TreeGoalsModel)