from django.urls import path, include
from AscentFlowHub_web import views

urlpatterns = [
    path('', views.index_page, name='index_page_path'),
    path('logout/', views.logout_handler, name='logout_path'),
    path('login/', views.LoginPageView.as_view(), name='login_page_path'),
    path('registration/', views.registration_page, name='registration_page_path')
]
