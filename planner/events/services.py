from datetime import datetime, timedelta
from dateutil.rrule import *
from dateutil.parser import *


def get_dates(metadata, start_date, end_date, event_start, event_end, end_repeat=None):
	saved_args = {**locals()}
	print("saved_args is", saved_args)
	start_date = parse(start_date)
	end_date = parse(end_date)
	print('Weekly: ', WEEKLY)
	interval = metadata['interval']
	# вычисляем дату начала для периодических событий
	if interval > 1 and event_end < datetime.date(start_date):
		# если событие повторяется по дням
		if metadata['freq'] == 3:
			# вычисляем количество дней между датой поиска (start_date) и датой начала события (event_start)
			days_delta = (datetime.date(start_date) - event_start).days
			# если не попали в интервал повторений, определяем новую дату начала повторений
			if days_delta % interval > 0:
				start_date += timedelta(days=interval-days_delta % interval)
		# если событие повторяется по неделям
		elif metadata['freq'] == 2:
			# определяем день недели даты начала события (event_start)
			event_weekday = event_start.weekday()
			# определяем день недели даты поиска (start_date)
			startdate_weekday = start_date.weekday()
			# определяем дату такого же дня недели, что и event_weekday, но на неделе, где идет поиск событий
			nearest_date = datetime.date(start_date) - timedelta(days=startdate_weekday - event_weekday)
			print('nearest_date', nearest_date)
			print('(nearest_date - event_start).days', (nearest_date - event_start).days)
			# если мы попали в нужную неделю, то оставляем start_date, если нет - вычисляем нужную неделю и в качестве старта берем понедельник
			if (nearest_date - event_start).days % (7 * interval) != 0:
				print('ku')
				start_date = (event_start + timedelta(days=7 * interval)) - timedelta(days=event_weekday)
	elif event_start > datetime.date(start_date) or event_start < datetime.date(start_date) <= event_end:
		start_date = event_start
	until = end_date if not end_repeat or datetime.date(end_date) <= end_repeat else end_repeat
	metadata['dtstart'] = start_date
	metadata['until'] = until
	print('start_date: ', start_date)
	return list(rrule(**metadata))


