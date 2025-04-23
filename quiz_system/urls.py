from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quizzes.urls')),           # your quiz app routes
   path('accounts/', include('django.contrib.auth.urls')),  # 🔐 built-in login/logout/password_reset
]
