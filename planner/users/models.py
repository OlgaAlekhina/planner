from django.db import models
from django.contrib.auth.models import User


USER_SEX = [
	('M', 'Male'),
	('F', 'Female'),
	('N', None)
]


class UserProfile(models.Model):
	""" Модель для хранения дополнительных данных пользователя """
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.CharField(max_length=200, blank=True)
	gender = models.CharField(max_length=1, choices=USER_SEX, blank=True)
	birthday = models.DateField(blank=True, null=True)
	nickname = models.CharField(max_length=50, blank=True)
	premium_end = models.DateField(blank=True, null=True)

	def __str__(self):
		return f"{self.user.username}-{self.user.id}"

	@property
	def default_groupuser_id(self):
		""" Добавляет идентификатор участника дефолтной группы к профилю пользователя """
		user = self.user
		try:
			default_group = user.group_set.get(default=True)
			default_groupuser = user.group_users.get(group=default_group)
			return default_groupuser.id
		except:
			return None


class Group(models.Model):
	""" Модель для хранения данных группы """
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	color = models.CharField(max_length=50)
	default = models.BooleanField(default=False)

	# добавила, так как был инцидент с созданием 2-х дефолтных групп, что привело к критическим ошибкам при авторизации
	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['owner'],
				condition=models.Q(default=True),
				name='unique_default_group_per_user'
			)
		]

	def __str__(self):
		return f"group-{self.id}-({self.owner.username})-default" if self.default else f"group-{self.id}-({self.owner.username})"


class GroupUser(models.Model):
	""" Модель для хранения данных участников группы """
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_users')
	group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='users')
	user_name = models.CharField(max_length=30)
	user_role = models.CharField(max_length=30, blank=True, null=True)
	user_color = models.CharField(max_length=30, blank=True, null=True)

	def __str__(self):
		return f"group-{self.group.id}, user{self.id}-{self.user_name}"


class SignupCode(models.Model):
	""" Модель для хранения кодов, высылаемых при регистрации и восстановлении пароля """
	code = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	code_time = models.DateTimeField(auto_now_add=True)




