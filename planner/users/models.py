from django.db import models
from django.contrib.auth.models import User


USER_SEX = [
	('M', 'Male'),
	('F', 'Female'),
	('N', None)
]


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.ImageField(upload_to="avatars", blank=True)
	gender = models.CharField(max_length=1, choices=USER_SEX, blank=True)
	birthday = models.DateField(blank=True, null=True)
	ya_login = models.CharField(max_length=50, blank=True)

	def __str__(self):
		return self.user.username


