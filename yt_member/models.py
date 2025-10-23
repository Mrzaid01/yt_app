from django.db import models

class UserAccount(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed password store karna best practice hai

    def __str__(self):
        return self.username
