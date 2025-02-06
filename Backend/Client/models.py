from django.db import models

STATUS_CHOICES = [
    (0, 'Online'),
    (1, 'Offline')
]


# Create your models here.
class Client(models.Model):
    ip = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    joined = models.DateTimeField(auto_now_add=True, auto_now=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return f"{self.name} {self.ip} {STATUS_CHOICES[self.status][1]}"
