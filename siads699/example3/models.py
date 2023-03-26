from django.db import models

class QuestionV3(models.Model):
    question_text = models.CharField(max_length=200)
    first_full_response = models.CharField(max_length=65535)
    first_approved_response = models.CharField(max_length=65535, null=True)
    second_full_response = models.CharField(max_length=65535, null=True)
    third_full_response = models.CharField(max_length=65535, null=True)
    execute_output = models.CharField(max_length=1000, null=True)
    status = models.IntegerField(default=99)
    user_rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=100)
    temperature = models.FloatField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.question_text}, status: {self.status}'

class UserComment(models.Model):
    question_obj = models.ForeignKey(QuestionV3, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.CharField(max_length=65535, blank=True)
    generated_full_response = models.CharField(max_length=65535, blank=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.question_obj.question_text} - {self.user_comment}"
