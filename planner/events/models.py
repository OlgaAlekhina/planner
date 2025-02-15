from django.db import models
from users.models import GroupUser


class Event(models.Model):
	title = models.CharField(max_length=100)
	user_role = models.CharField(max_length=30, blank=True)
	user_color = models.CharField(max_length=30, blank=True)

	def __str__(self):
		return f"group-{self.group.id}, user-{self.user_name}"


class EventUser(models.Model):
	user = models.ForeignKey(GroupUser, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)

	def __str__(self):
		return f"event-{self.event.id}, user-{self.user.user_name}"
