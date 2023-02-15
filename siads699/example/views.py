from django.http import HttpResponse
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
import openai

openai.api_key = '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'


def index(request):
    return HttpResponse("Hello, world. You're at the siads699 index.")


class InitialView(View):
    template_name = "example/initial.html"
    success_url = reverse_lazy('example:index')

    def get(self, request):
        response = request.session.get('response', False)
        if ( response ) : del(request.session['response'])
        ctx = {'response': response}

        return render(request, self.template_name, ctx)

    def post(self, request):
        question = request.POST['question']
        try:
            response = openai.Completion.create(
                model='davinci:ft-personal-2023-01-15-03-48-41',
                # prompt = question,
                #design the prompt to take in the question and the context
                # prompt = 'pretend to be a data analyst and read the df.' + question + '?',
                prompt='pretend to be a data analyst.' + question + '?',
                max_tokens=50,
                # n=1,
                # stop=None,
                # stop after the first sentence
                stop=['Sentence'],
                temperature=0.1,
                # frequency_penalty = 0.1
                # presence_penalty = 0.1
            )
        except:
            response = "well...,..."
        # ctx = {'response': response["choices"][0]["text"]}
        request.session['response'] = response["choices"][0]["text"]
        return redirect(request.path)

        return render(request, self.template_name, ctx)