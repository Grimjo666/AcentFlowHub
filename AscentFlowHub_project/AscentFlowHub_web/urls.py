from django.urls import path, include
from AscentFlowHub_web import views

urlpatterns = [
    path('', views.index_page, name='index_page_path'),
    path('logout/', views.logout_handler, name='logout_path'),
    path('login/', views.login_page, name='login_page_path')
]
