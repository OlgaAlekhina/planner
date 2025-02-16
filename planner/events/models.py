from django.db import models
from users.models import GroupUser


class Event(models.Model):
	title = models.CharField(max_length=100)
	location = models.CharField(max_length=100, blank=True)
	start_date = models.DateField()
	end_date = models.DateField()
	start_time = models.TimeField(blank=True, null=True)
	end_time = models.TimeField(blank=True, null=True)
	repeats = models.BooleanField(default=False)

	def __str__(self):
		return f"group-{self.group.id}, user-{self.user_name}"


class EventMeta(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	start_date = models.DateField()
	end_date = models.DateField()
	interval = models.IntegerField()


class EventUser(models.Model):
	user = models.ForeignKey(GroupUser, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)

	def __str__(self):
		return f"event-{self.event.id}, user-{self.user.user_name}"
