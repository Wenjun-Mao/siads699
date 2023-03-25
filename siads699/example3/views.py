from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import QuestionV3, UserComment

from django.http import HttpResponse

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
        ctx = {'answer_text': answer_text, 'question_text': question_text}

        return render(request, self.template_name, ctx)

    def post(self, request):
        question_text = request.POST.get('question_text', False)
        first_prompt = create_prompt(df, stage=1, question=question_text)
        # print('first_prompt: ', first_prompt)
        try:
            full_response_1, model, temperature = get_openai_response(first_prompt)
            answer_content_1 = full_response_1['choices'][0]['message']['content'].strip()
            if answer_content_1 == "__irrelevant__":
                status = 1
            else:
                status = 0
            question_obj = QuestionV3.objects.create(
                question_text=question_text,
                first_full_response=full_response_1,
                model=model,
                temperature=temperature,
                status=status
            )
        except Exception as e:
            # print("Error in get_openai_response", e)
            answer_content_1 = "Sorry, I cannot answer your question. Please try again."

        request.session['question_id'] = question_obj.id
        request.session['answer_text'] = answer_content_1
        request.session['question_text'] = question_text

        return redirect(request.path)


class Step2ProcessView(View):
    def post(self, request, *args, **kwargs):
        # handle the POST request here
        return redirect('example3:ask_question')

class Step2AddCommentView(View):
    def post(self, request, *args, **kwargs):
        # handle the POST request here
        question_text = request.POST.get('question_text', False)
        answer_text = request.POST.get('answer_text', False)
        comment_text = request.POST.get('comment_text', False)
        question_obj = request.session.get('question_obj', False)
        first_prompt_new = create_prompt(df, stage=1, question=question_text, comments=comment_text, first_answer=answer_text)
        full_response_1_new, _, _ = get_openai_response(first_prompt_new)
        answer_content_1_new = full_response_1_new['choices'][0]['message']['content'].strip()

        question_obj = QuestionV3.objects.get(id=request.session.get('question_id'))
        print('question_obj.id: ', question_obj.id)

        comment_obj = UserComment.objects.create(
            question=question_obj,
            comment_text=comment_text,
            generated_response=answer_content_1_new
        )
        request.session['answer_text'] = answer_content_1_new
        request.session['comment_id'] = comment_obj.id

        return redirect('example3:ask_question')



class ProcessAgreementView(View):
    def post(self, request, question_id):
        question = get_object_or_404(QuestionV3, id=question_id)

        # Step 2: Get second_full_response
        accepted_answer = question.first_approved_response if question.first_approved_response else question.first_full_response['choices'][0]['message']['content'].strip()
        second_prompt = create_prompt(df, stage=2, question=question.question_text, first_answer=accepted_answer)
        second_full_response, _, _ = get_openai_response(second_prompt)
        answer_content_2 = second_full_response['choices'][0]['message']['content'].strip()

        try:
            output = get_execute_output(answer_content_2)
            question.second_full_response = second_full_response
            question.output = output
            question.save()

            # Step 3: Get third_full_response
            third_prompt = create_prompt(df, stage=3, question=question.question_text,
                                          first_answer=accepted_answer, second_answer=answer_content_2, output=output)
            third_full_response, _, _ = get_openai_response(third_prompt)
            question.third_full_response = third_full_response
            question.status = 0
            question.save()

        except Exception as e:
            question.second_full_response = second_full_response
            question.status = 2
            question.save()
            return redirect('example3:ask_question', question_id=question.id)

        return redirect('example3:ask_question', question_id=question.id)



def handle_disagreement(question, user_comment):
    first_answer = question.first_approved_response if question.first_approved_response else question.first_full_response['choices'][0]['message']['content'].strip()
    new_prompt = create_prompt(df, stage=1, question=question.question_text, first_answer=first_answer, comments=user_comment)
    new_response, _, _ = get_openai_response(new_prompt)
    answer_regen = new_response['choices'][0]['message']['content'].strip()

    return answer_regen


class UserCommentView(View):
    def post(self, request, question_id):
        form = UserCommentForm(request.POST)
        question = get_object_or_404(QuestionV3, id=question_id)

        if form.is_valid():
            user_comment = form.cleaned_data['user_comment']
            accepted = form.cleaned_data['accepted']

            if accepted:
                question.first_approved_response = question.first_full_response
                question.save()
            else:
                user_comment_instance = UserComment.objects.create(
                    question=question,
                    user_comment=user_comment
                )

                new_prompt = create_prompt(question.question_text, user_comment=user_comment_instance.user_comment, stage=1)
                generated_response, model, temperature = get_openai_response(new_prompt)
                answer_content = generated_response['choices'][0]['message']['content'].strip()

                user_comment_instance.generated_response = generated_response
                user_comment_instance.save()

            user_comment_form = UserCommentForm(initial={'question': question.id})
            return render(request, 'example3/query.html', {'question': question, 'user_comment_form': user_comment_form, 'answer_content': answer_content})

        return render(request, 'example3/query.html', {'question': question, 'form': form})


class AcceptResponseView(View):
    def post(self, request, question_id, comment_id):
        question = get_object_or_404(QuestionV3, id=question_id)
        comment = get_object_or_404(UserComment, id=comment_id)

        comment.accepted = True
        comment.save()

        if not question.first_approved_response:
            question.first_approved_response = comment.generated_response
            question.save()

        return redirect('example3:ask_question')
