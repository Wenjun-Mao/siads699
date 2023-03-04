from django.db import models

# Create your models here.
class Question(models.Model):
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.question