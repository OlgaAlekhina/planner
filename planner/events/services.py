from datetime import datetime
from dateutil.rrule import *
from dateutil.parser import *


def get_dates(metadata, start_date, end_date, event_start, event_end=None):
	saved_args = {**locals()}
	print("saved_args is", saved_args)
	if metadata['daily']:
		freq = DAILY
	elif metadata['weekly']:
		freq = WEEKLY
	elif metadata['monthly']:
		freq = MONTHLY
	else:
		freq = YEARLY
	start_date = parse(start_date)
	end_date = parse(end_date)
	if not event_end or datetime.date(end_date) <= event_end:
		until = end_date
	else:
		until = event_end
	print('until', until)
	params = {
		'freq': freq,
		'dtstart': start_date,
		'until': until
	}
	return list(rrule(**params))


