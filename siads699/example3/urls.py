from django.urls import path
from . import views

app_name = 'example3'

# urlpatterns = [
#     path('ask_question/', views.AskQuestionView.as_view(), name='ask_question'),
#     path('comment/<int:question_id>/', views.HandleCommentView.as_view(), name='handle_comment'),
#     path('accept/<int:question_id>/<int:comment_id>/', views.AcceptResponseView.as_view(), name='accept_response'),
# ]

urlpatterns = [
    path('', views.Step1AskQuestionView.as_view(), name='ask_question'),
    path('accept_answer', views.Step2ProcessView.as_view(), name='accept_answer'),
    path('addcomment', views.Step2AddCommentView.as_view(), name='add_comment'),
    path('list/', views.QuestionListView.as_view(), name='question_list'),
]