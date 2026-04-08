from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name="home"),
    path('create_league/', views.crea_lega_view, name="create_league")
]