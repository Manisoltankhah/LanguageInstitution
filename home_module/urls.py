from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('rules/', views.RuleView.as_view(), name='rules'),
    path('about-us/', views.AboutView.as_view(), name='about_us'),
]