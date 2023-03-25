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
    # path('question/int:question_id/', views00.QuestionDetailView.as_view(), name='question_detail'),
    # path('question/int:question_id/accept/', views00.accept_answer, name='accept_answer'),
    # path('question/int:question_id/retry/', views00.retry_second_step, name='retry_second_step'),
    # path('question/int:question_id/proceed_to_third_step/', views00.proceed_to_third_step, name='proceed_to_third_step'),
    # path('question/int:question_id/accept_third_answer/', views00.accept_third_answer, name='accept_third_answer'),
    # path('question/int:question_id/reject_third_answer/', views00.reject_third_answer, name='reject_third_answer'),
]