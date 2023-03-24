from django.urls import path
from . import views

app_name = 'example3'

urlpatterns = [
    path('ask_question/', views.AskQuestionView.as_view(), name='ask_question'),
    path('comment/<int:question_id>/', views.HandleCommentView.as_view(), name='handle_comment'),
    path('accept/<int:question_id>/<int:comment_id>/', views.AcceptResponseView.as_view(), name='accept_response'),
]