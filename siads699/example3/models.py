from django.db import models

# Create your models here.
class QuestionV3(models.Model):
    model = models.CharField(max_length=100)
    questionID = models.IntegerField()
    question = models.CharField(max_length=200)
    first_full_response = models.CharField(max_length=65535)
    second_full_response = models.CharField(max_length=65535)
    third_full_response = models.CharField(max_length=65535)
    output = models.CharField(max_length=1000)
    third_answer = models.CharField(max_length=65535)
    status = models.IntegerField()
    temperature = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.question