from django.shortcuts import render, get_object_or_404, redirect
from django.views import View, generic
from .models import QuestionV3, UserComment

import json

# from .forms import AskQuestionForm, UserCommentForm
from .chatgpt_utils699_web import create_prompt, get_openai_response, get_execute_output

import pandas as pd
import openai
from sqlalchemy import create_engine
from sqlalchemy import text
openai.api_key = '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'

######### Prepare data #########
import os

csv_file = os.path.join(os.path.dirname(__file__), 'assets', 'Online_Retail_1000_v2.csv')

df = pd.read_csv(csv_file)
# Calculate total sales and add as a new column
df['TotalSales'] = df['Quantity'] * df['UnitPrice']
temp_db = create_engine('sqlite:///:memory:', echo=False)
data = df.to_sql(name='df', con=temp_db)

######### The Views #########
class Step1AskQuestionView(View):
    template_name = "example3/query_main.html"
    def get(self, request):
        answer_text = request.session.get('answer_text', False)
        question_text = request.session.get('question_text', False)
        status_code = request.session.get('status', False)
        ctx = {'answer_text': answer_text, 'question_text': question_text, 'status_code': status_code}

        return render(request, self.template_name, ctx)

    def post(self, request):

        question_obj, status = None, None
        print(f"Openai-api-key")
        print(openai.api_key)

        question_text = request.POST.get('question_text', False)
        first_prompt = create_prompt(df, stage=1, question=question_text)
        model_selected = request.POST.get('model_selected', False)
        temperature_selected_str = float(request.POST.get('temperature_selected', False))
        try:
            temperature_selected = float(temperature_selected_str)
        except ValueError:
            # Handle the error, e.g., set a default value or return an error message
            temperature_selected = 0.2

        try:
            full_response_1, model, temperature = get_openai_response(first_prompt, model=model_selected, temperature=temperature_selected)
            answer_content_1 = full_response_1['choices'][0]['message']['content'].strip()
            if answer_content_1 == "__irrelevant__":
                status = 1
            else:
                status = 99
            question_obj = QuestionV3.objects.create(
                question_text=question_text,
                first_full_response=full_response_1,
                model=model,
                temperature=temperature,
                status=status
            )
        except Exception as e:
            answer_content_1 = f"Sorry, I cannot answer your question. Please try again. {e}"
            print(f"Er......{answer_content_1}")

        try:
            request.session['question_id'] = question_obj.id
        except:
            print(answer_content_1)
        request.session['answer_text'] = answer_content_1
        request.session['question_text'] = question_text
        # clear the comment_id so it doesn't get carried over to the next question
        request.session['comment_id'] = False
        request.session['status_code'] = status

        return redirect(request.path)


class Step2ProcessView(View):
    def post(self, request, *args, **kwargs):
        comment_id = request.session.get('comment_id', False)
        # Get the comment object and set accepted to True
        if comment_id:
            comment_obj = UserComment.objects.get(id=comment_id)
            comment_obj.accepted = True
            comment_obj.save()

        question_id = request.session.get('question_id', False)
        question_obj = QuestionV3.objects.get(id=question_id)
        # Save the first approved response
        if comment_id:
            question_obj.first_approved_response = comment_obj.generated_full_response
        else:
            question_obj.first_approved_response = question_obj.first_full_response
        question_obj.save() ##########

        answer_text = json.loads(question_obj.first_approved_response)['choices'][0]['message']['content'].strip()
        question_text = question_obj.question_text

        second_prompt = create_prompt(df, stage=2, question=question_text, first_answer=answer_text)
        second_full_response, _, _ = get_openai_response(second_prompt, model=question_obj.model, temperature=question_obj.temperature)
        answer_content_2 = second_full_response['choices'][0]['message']['content'].strip()
        try:
            execute_output = get_execute_output(answer_content_2, temp_db)
        except Exception as e:
            print("Error in get_execute_output", e)
            execute_output = "Error"

        question_obj.execute_output = execute_output
        question_obj.second_full_response = second_full_response

        if execute_output == "Error":
            question_obj.status = 2
            question_obj.save()
            current_answer = "Sorry, error execute_output."
            ###### Let user retry??????????????? ######
        else:
            question_obj.status = 0
            third_prompt = create_prompt(df, stage=3, question=question_text, first_answer=answer_text, second_answer=answer_content_2, output=execute_output)
            third_full_response, _, _ = get_openai_response(third_prompt, model=question_obj.model, temperature=question_obj.temperature)
            answer_content_3 = third_full_response['choices'][0]['message']['content'].strip()
            question_obj.third_full_response = third_full_response
            question_obj.save()
            current_answer = answer_content_3

        request.session['question_text'] = question_text
        request.session['answer_text'] = current_answer
        request.session['question_id'] = question_obj.id
        request.session['comment_id'] = comment_id
        request.session['status_code'] = question_obj.status

        return redirect('example3:ask_question')

class Step2AddCommentView(View):
    def post(self, request, *args, **kwargs):
        comment_text = request.POST.get('comment_text', False)
        question_obj = QuestionV3.objects.get(id=request.session.get('question_id'))
        question_text = question_obj.question_text
        answer_text = json.loads(question_obj.first_full_response)['choices'][0]['message']['content'].strip()
        first_prompt_new = create_prompt(df, stage=1, question=question_text, comments=comment_text, first_answer=answer_text)
        full_response_1_new, _, _ = get_openai_response(first_prompt_new, model=question_obj.model, temperature=question_obj.temperature)
        answer_content_1_new = full_response_1_new['choices'][0]['message']['content'].strip()

        comment_obj = UserComment.objects.create(
            question_obj=question_obj,
            comment_text=comment_text,
            generated_full_response=full_response_1_new
        )
        request.session['answer_text'] = answer_content_1_new
        request.session['comment_id'] = comment_obj.id

        return redirect('example3:ask_question')


class QuestionListView(generic.ListView):
    model = QuestionV3
    paginate_by = 5
    template_name = 'example3/question_list.html'

class QuestionListViewFull(generic.ListView):
    model = QuestionV3
    paginate_by = 5
    template_name = 'example3/question_list_full.html'


from django.http import JsonResponse

def update_user_rating(request):
    if request.method == 'POST':
        question_id = request.session.get('question_id')
        user_rating = request.POST.get('user_rating')

        question = QuestionV3.objects.get(pk=question_id)
        question.user_rating = int(user_rating)
        question.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})
