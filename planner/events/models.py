from django.db import models
from django.contrib.auth.models import User


EVENT_FREQ = [
	(3, 'Daily'),
	(2, 'Weekly'),
	(1, 'Monthly'),
	(0, 'Yearly')
]

MONTHS = [
	(0, None),
	(1, 'January'),
	(2, 'Fabruary'),
	(3, 'March'),
	(4, 'April'),
	(5, 'May'),
	(6, 'June'),
	(7, 'July'),
	(8, 'August'),
	(9, 'September'),
	(10, 'October'),
	(11, 'November'),
	(12, 'December')
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
	freq = models.IntegerField(choices=EVENT_FREQ)
	interval = models.IntegerField(default=1)
	byweekday = models.CharField(max_length=50, blank=True, null=True)
	bymonthday = models.CharField(max_length=50, blank=True, null=True)
	bymonth = models.IntegerField(choices=MONTHS, blank=True, null=True)
	byweekno = models.IntegerField(blank=True, null=True)

	def __str__(self):
		return f"event{self.event.id}, {self.event.title}"


class CanceledEvent(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	cancel_date = models.DateField()

	def __str__(self):
		return f"event{self.event.id}, {self.event.title}-{self.cancel_date}"



