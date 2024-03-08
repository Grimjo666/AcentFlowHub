from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from AscentFlowHub_API.views import *


router = routers.SimpleRouter()
router.register(r'life-category', LifeCategoryViewSet, basename='life_category_path')
router.register(r'tree-goals', TreeGoalsViewSet, basename='tree_goals_path')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),
    path('', include('AscentFlowHub_web.urls'))
]
