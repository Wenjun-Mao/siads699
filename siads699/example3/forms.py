from django import forms
from .models import UserComment

class UserCommentForm(forms.ModelForm):
    class Meta:
        model = UserComment
        fields = ['user_comment']
        labels = {
            'user_comment': 'Your Comment',
        }
        widgets = {
            'user_comment': forms.Textarea(attrs={'cols': 40, 'rows': 4}),
        }

class AskQuestionForm(forms.Form):
    question = forms.CharField(
        label='Your question',
        max_length=200,
        widget=forms.Textarea(attrs={'rows': 3})
        )