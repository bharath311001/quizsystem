from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('history/', views.score_history, name='score_history'),
    path('upload-frame/', views.upload_frame, name='upload_frame'),
    path('signup/', views.signup_view, name='signup'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('set-new-password/', views.set_new_password_view, name='set_new_password'),
    path('admin-login/', views.admin_login_view, name='admin_login'),



]
