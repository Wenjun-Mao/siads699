from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import QuestionV3, UserComment
from .forms import AskQuestionForm, UserCommentForm

from .forms import AskQuestionForm, UserCommentForm
from .chatgpt_utils699_web import create_prompt, get_openai_response, get_execute_output

import pandas as pd
import openai
from sqlalchemy import create_engine
from sqlalchemy import text
openai.api_key = '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'

######### Prepare data #########
import os

csv_file = os.path.join(os.path.dirname(__file__), 'Online_Retail_1000_v2.csv')

df = pd.read_csv(csv_file)
# Calculate total sales and add as a new column
df['TotalSales'] = df['Quantity'] * df['UnitPrice']
temp_db = create_engine('sqlite:///:memory:', echo=False)
data = df.to_sql(name='df', con=temp_db)

######### The Views #########
class AskQuestionView(View):
    def get(self, request):
        form = AskQuestionForm()
        return render(request, 'example3/ask_question.html', {'form': form})

    def post(self, request):
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            question_text = form.cleaned_data['question']
            prompt = create_prompt(df, 1, question_text, language='SQL')
            full_response, model, temperature = get_openai_response(prompt)
            answer_content = full_response['choices'][0]['message']['content'].strip()

            question = QuestionV3(
                question_text=question_text,
                first_full_response=full_response,
                model=model,
                temperature=temperature,
            )

            if answer_content == "__irrelevant__":
                question.status = 1
            else:
                question.status = None

            question.save()

            return redirect('question_detail', question_id=question.id)

        return render(request, 'example3/ask_question.html', {'form': form})

class QuestionDetailView(View):
    def get(self, request, question_id):
        question = get_object_or_404(QuestionV3, id=question_id)
        answer_content = question.first_full_response['choices'][0]['message']['content'].strip()
        form = UserCommentForm()
        return render(request, 'example3/question_detail.html', {
            'question': question,
            'answer_content': answer_content,
            'form': form
        })

    def post(self, request, question_id):
        question = get_object_or_404(QuestionV3, id=question_id)
        form = UserCommentForm(request.POST)
        first_answer = question.first_approved_response or question.first_full_response
        answer_content = first_answer['choices'][0]['message']['content'].strip()

        if form.is_valid():
            user_comment = form.cleaned_data['comment']
            prompt = create_prompt(df, 1, question.question_text, first_answer=answer_content, comments=user_comment, language='SQL')
            full_response, _, _ = get_openai_response(prompt)
            answer_regen = full_response['choices'][0]['message']['content'].strip()

            user_comment_obj = UserComment(
                question=question,
                user_comment=user_comment,
                generated_response=answer_regen
            )
            user_comment_obj.save()

            return redirect('question_detail', question_id=question.id)

        return render(request, 'example3/question_detail.html', {
            'question': question,
            'answer_content': answer_content,
            'form': form
        })

def accept_answer(request, question_id):
    question = get_object_or_404(QuestionV3, id=question_id)
    if request.method == 'POST':
        answer_content = question.first_full_response['choices'][0]['message']['content'].strip()
        question.first_approved_response = answer_content
        question.save()
        prompt = create_prompt(df, 2, question.question_text, first_answer=answer_content, language='SQL')
        full_response, _, _ = get_openai_response(prompt)
        second_answer = full_response['choices'][0]['message']['content'].strip()

        try:
            output = get_execute_output(second_answer, temp_db)
            question.output = output
            question.status = 0
        except Exception as e:
            question.status = 2

        question.second_full_response = full_response
        question.save()

        return redirect('question_detail', question_id=question.id)

    return render(request, 'example3/question_detail.html', {'question': question})

def retry_second_step(request, question_id):
    question = get_object_or_404(QuestionV3, id=question_id)
    if request.method == 'POST':
        first_answer = question.first_approved_response or question.first_full_response
        answer_content = first_answer['choices'][0]['message']['content'].strip()
        prompt = create_prompt(df, 2, question.question_text, first_answer=answer_content, language='SQL')
        full_response, _, _ = get_openai_response(prompt)
        second_answer = full_response['choices'][0]['message']['content'].strip()

        try:
            output = get_execute_output(second_answer, temp_db)
            question.output = output
            question.status = 0
        except Exception as e:
            question.status = 2

        question.second_full_response = full_response
        question.save()

        return redirect('question_detail', question_id=question.id)

    return render(request, 'example3/question_detail.html', {'question': question})

def proceed_to_third_step(request, question_id):
    question = get_object_or_404(QuestionV3, id=question_id)
    if request.method == 'POST':
        first_answer = question.first_approved_response or question.first_full_response
        first_answer_content = first_answer['choices'][0]['message']['content'].strip()
        second_answer = question.second_full_response
        second_answer_content = second_answer['choices'][0]['message']['content'].strip()
        output = question.output
        prompt = create_prompt(df, 3, question.question_text, first_answer=first_answer_content, second_answer=second_answer_content, output=output, language='SQL')
        full_response, _, _ = get_openai_response(prompt)
        third_answer = full_response['choices'][0]['message']['content'].strip()

        question.third_full_response = full_response
        question.third_answer = third_answer
        question.save()

        return redirect('question_detail', question_id=question.id)

    return render(request, 'example3/question_detail.html', {'question': question})

def accept_third_answer(request, question_id):
    question = get_object_or_404(QuestionV3, id=question_id)
    if request.method == 'POST':
        question.status = 0
        question.save()
        return redirect('question_detail', question_id=question.id)

    return render(request, 'example3/question_detail.html', {'question': question})

def reject_third_answer(request, question_id):
    question = get_object_or_404(QuestionV3, id=question_id)
    if request.method == 'POST':
        question.status = 3
        question.save()
        return redirect('question_detail', question_id=question.id)

    return render(request, 'example3/question_detail.html', {'question': question})
