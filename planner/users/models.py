from django.db import models
from django.contrib.auth.models import User


USER_SEX = [
	('M', 'Male'),
	('F', 'Female'),
	('N', None)
]


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.CharField(max_length=200, blank=True)
	gender = models.CharField(max_length=1, choices=USER_SEX, blank=True)
	birthday = models.DateField(blank=True, null=True)
	nickname = models.CharField(max_length=50, blank=True)

	def __str__(self):
		return self.user.username


class Group(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)

	def __str__(self):
		return f"group-{self.id}"


class GroupUser(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_users')
	user_name = models.CharField(max_length=30)
	user_role = models.CharField(max_length=30, blank=True)
	user_color = models.CharField(max_length=30)

	def __str__(self):
		return f"group-{self.group.id}, user-{self.user_name}"


class SignupCode(models.Model):
	code = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	code_time = models.DateTimeField(auto_now_add=True)




