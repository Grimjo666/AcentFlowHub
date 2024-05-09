from django.urls import path
from frontend import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index_page, name='index_page'),
    path('page-not-found/', views.page_not_found, name='page_not_found'),
    path('logout/', views.LogoutView.as_view(), name='logout_path'),
    path('login/', views.LoginPageView.as_view(), name='login_page'),
    path('registration/', views.registration_page, name='registration_page'),
    path('my-progress/', views.MyProgressPageView.as_view(), name='my_progress_page'),
    path('my-progress/<slug:category_name>', views.SphereOfLifePageView.as_view(), name='sphere_of_life_page'),
    path('my-progress/sub_goal/<int:sub_goal_id>', views.SubGoalPageView.as_view(), name='sub_goal_page'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/change_photo/', views.ChangeProfilePhotoView.as_view(), name='change_profile_photo'),
    path('test-page/', views.test_page)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
