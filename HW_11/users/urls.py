from django.urls import path, include
from . import views
# from .views import logout_view


app_name = "users"
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    # path('logout/', logout_view, name='logout'),
]