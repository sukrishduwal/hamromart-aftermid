from django.conf import settings
from django.db import models


class UserSession(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    session_key = models.CharField(max_length=40)