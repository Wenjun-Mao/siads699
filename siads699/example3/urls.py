from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('example3/', views.InitialView.as_view(), name='initial3'),
    path('example3_list/', views.QuestionListView.as_view(), name='questions3'),
]