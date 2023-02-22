from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('example2/', views.InitialView.as_view(), name='initial2'),
    path('example2_list/', views.QuestionListView.as_view(), name='questions'),
]