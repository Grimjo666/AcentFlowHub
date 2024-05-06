from django.urls import path, include
from frontend import views

urlpatterns = [
    path('', views.index_page, name='index_page'),
    path('page-not-found/', views.page_not_found, name='page_not_found'),
    path('logout/', views.LogoutView.as_view(), name='logout_path'),
    path('login/', views.LoginPageView.as_view(), name='login_page'),
    path('registration/', views.registration_page, name='registration_page'),
    path('my-progress/', views.MyProgressPageView.as_view(), name='my_progress_page'),
    path('my-progress/<slug:category_name>', views.SphereOfLifePageView.as_view(), name='sphere_of_life_page'),
    path('my-progress/sub_goal/<int:sub_goal_id>', views.SubGoalPageView.as_view(), name='sub_goal_page'),
    path('test-page/', views.test_page)
]
