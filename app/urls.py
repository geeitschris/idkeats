from django.urls import path
from . import views

# NO LEADING SLASHES
urlpatterns = [
    path('', views.index, name='index'),
    path('createuser', views.createuser),
    path('login', views.login),
    path('success', views.dashboard),
    path('logout', views.logout),
    path('favorites/<str:id>', views.favorites),
    path('favorite/<str:id>', views.addfavorites),
    path('favorites/add/<str:id>/success', views.favorites),
    path('remove/<str:bizid>', views.removeFave),
    path('register', views.register),
    path('random/<lat>/<lng>', views.decideForMe),
]
