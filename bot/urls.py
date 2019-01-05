from django.urls import path
from . import views

# 用來串接callback主程式
urlpatterns = [
    path('callback/', views.callback),
]