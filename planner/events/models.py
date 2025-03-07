from django.db import models
from django.contrib.auth.models import User


EVENT_FREQ = [
	('DAILY', 'Daily'),
	('WEEKLY', 'Weekly'),
	('MONTHLY', 'Monthly'),
	('YEARLY', 'Yearly')
]

class Event(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100)
	location = models.CharField(max_length=100, blank=True, null=True)
	start_date = models.DateField()
	end_date = models.DateField()
	start_time = models.TimeField(blank=True, null=True)
	end_time = models.TimeField(blank=True, null=True)
	repeats = models.BooleanField(default=False)
	end_repeat = models.DateField(blank=True, null=True)
	users = models.ManyToManyField(User, related_name='events')

	def __str__(self):
		return f"event{self.id}, {self.title}"


class EventMeta(models.Model):
	event = models.OneToOneField(Event, on_delete=models.CASCADE)
	freq = models.CharField(max_length=7, choices=EVENT_FREQ)
	interval = models.IntegerField(default=1)
	byweekday = models.CharField(max_length=50, blank=True, null=True)
	bymonthday = models.CharField(max_length=50, blank=True, null=True)

	def __str__(self):
		return f"event{self.event.id}, {self.event.title}"
