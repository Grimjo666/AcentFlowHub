from django.urls import path, include
from AscentFlowHub_web import views

urlpatterns = [
    path('', views.index_page, name='index_page_path'),
    path('page-not-found/', views.page_not_found, name='page_not_found_path'),
    path('logout/', views.LogoutView.as_view(), name='logout_path'),
    path('login/', views.LoginPageView.as_view(), name='login_page_path'),
    path('registration/', views.registration_page, name='registration_page_path'),
    path('my-progress/', views.MyProgressPageView.as_view(), name='my_progress_page_path')
]
