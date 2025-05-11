from django.urls import path, include
# from .views import logout_view


app_name = "users"
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    # path('logout/', logout_view, name='logout'),
]