from django.contrib import admin

from api import models as api_models
from frontend import models as web_models

admin.site.register(api_models.LifeCategory)
admin.site.register(api_models.TreeGoals)
admin.site.register(api_models.ManualUser)
admin.site.register(web_models.UserTraining)
admin.site.register(web_models.UserSettings)
