from django.urls import path
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView

from .views import *

urlpatterns = [
    path('', RubricsListView.as_view(), name='index'),
    path('<str:page>/', other_page, name='other'),
    path('accounts/login/', BulBoardLoginView.as_view(), name='login'),
    path('accounts/profile/<int:pk>', UserProfileView.as_view(), name='profile'),
    path('accounts/login/', BulBoardLoginView.as_view(), name='login'),
    path('accounts/profile/change/', ChangeUserProfileView.as_view(), name='profile_change'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/password/change/', BulBoardPasswordChangeView.as_view(), name='password_change'),
    path('accounts/logout/', BulBoardLogoutView.as_view(), name='logout'),
    path('accounts/registration/done/', RegistrationDoneView.as_view(), name='registration_done'),
    path('accounts/registration/', RegistrateUserView.as_view(), name='registration'),
    path('accounts/registration/activate/<str:sign>/', user_activate, name='registration_activate'),
    path('accounts/password/reset/', ResetUserPasswordView.as_view(), name='password_reset'),
    path('accounts/password/reset/done/', PasswordResetDoneView.as_view(template_name='reset_email_sent.html'), name='password_reset_done'),
    path('accounts/password/reset/confirm/<str:uidb64>/<str:token>', PasswordResetConfirmView.as_view(template_name='reset_password_confirm.html'),
                                                                                                                 name='password_reset_confirm'),
    path('accounts/password/reset/complete/', PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'),
                                                                                        name='password_reset_complete'),
    path('rubric/<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:from_view>/<int:pk>/', bulletin_detail, name='detail'),
    path('adverts/users/', user_adverts, name='user_adverts'),
    path('adverts/add/', add_bulletin, name='add_bulletin'),
    path('adverts/update/<int:pk>/', update_bulletin, name='update_bulletin'),
    path('adverts/delete/<int:pk>/', BulletinDeleteView.as_view(), name='delete_bulletin'),
]
