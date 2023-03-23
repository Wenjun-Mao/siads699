from django.http import HttpResponse
from django.views import View, generic
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
import openai

from example3.models import QuestionV3

openai.api_key = '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'


def index(request):
    return HttpResponse("Hello, world. You're at the siads699 index.")


class InitialView(View):
    template_name = "example3/query.html"
    success_url = reverse_lazy('example:index')

    def get(self, request):
        response = request.session.get('response', False)
        question = request.session.get('question', False)
        ctx = {'response': response, 'question': question}

        return render(request, self.template_name, ctx)

    def post(self, request):
        question = request.POST['question']
        try:
            response = openai.Completion.create(
                model='davinci:ft-personal-2023-01-15-03-48-41',
                prompt='pretend to be a data analyst.' + question + '?',
                max_tokens=50,
                stop=['Sentence'],
                temperature=0.8,
            )
            response_text = response["choices"][0]["text"]
        except:
            response_text = "well......something was wrong on OpenAI's end.  Try again later."
        # ctx = {'response': response["choices"][0]["text"]}
        request.session['response'] = response_text
        request.session['question'] = question

        # Save to database
        QuestionV3.objects.create(question=question, answer=response_text)

        return redirect(request.path)



class QuestionListView(generic.ListView):
    model = QuestionV3
    paginate_by = 5
