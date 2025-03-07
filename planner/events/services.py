from datetime import datetime, timedelta
from dateutil.rrule import *
from dateutil.parser import *


def get_dates(metadata, start_date, end_date, event_start, event_end, end_repeat=None):
	saved_args = {**locals()}
	print("saved_args is", saved_args)
	start_date = parse(start_date)
	end_date = parse(end_date)
	interval = metadata['interval']
	if interval > 1 and event_end < datetime.date(start_date):
		if metadata['freq'] == 3:
			days_delta = (datetime.date(start_date) - event_start).days
			if days_delta % interval > 0:
				start_date += timedelta(days=interval-days_delta % interval)
	elif event_start > datetime.date(start_date) or event_start < datetime.date(start_date) <= event_end:
		start_date = event_start
	until = end_date if not end_repeat or datetime.date(end_date) <= end_repeat else end_repeat
	metadata['dtstart'] = start_date
	metadata['until'] = until
	return list(rrule(**metadata))


