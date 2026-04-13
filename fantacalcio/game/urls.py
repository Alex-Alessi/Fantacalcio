from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name="home"),
    path('create_league/', views.crea_lega_view, name="create_league"),
    path('search_league/', views.join_lega_view, name="search_league"),
    path('<int:pk>/detail_league/', views.dettaglio_lega, name="detail_league"),
    path('<int:pk>/dashboard_squadra/', views.dashboard_squadra, name="dashboard_squadra"),
    path('join_squadra', views.join_squadra, name="join_squadra")
]