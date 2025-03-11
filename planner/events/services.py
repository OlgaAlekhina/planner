from datetime import datetime, timedelta
from dateutil.rrule import *
from dateutil.parser import *
from dateutil.relativedelta import relativedelta


def get_dates(metadata, filter_start, filter_end, event_start, event_end, end_repeat=None):
	""" Функция для вычисления списка дат для повторяющихся событий с помощью библиотеки rrule """
	saved_args = {**locals()}
	print("saved_args is", saved_args)
	filter_start = parse(filter_start)
	filter_end = parse(filter_end)
	print('Monthly: ', MONTHLY)
	interval = metadata['interval']
	# вычисляем дату начала для периодических событий
	if interval > 1 and event_end < datetime.date(filter_start):
		# если событие повторяется по дням
		if metadata['freq'] == 3:
			# вычисляем количество дней между стартовой датой поиска (filter_start) и датой начала события (event_start)
			days_delta = (datetime.date(filter_start) - event_start).days
			# если не попали в интервал повторений, определяем новую дату начала повторений
			if days_delta % interval > 0:
				filter_start += timedelta(days=interval-days_delta % interval)
		# если событие повторяется по неделям
		elif metadata['freq'] == 2:
			print((datetime.date(filter_start) - event_start).days)
			# определяем день недели даты начала события (event_start)
			event_weekday = event_start.weekday()
			# определяем день недели стартовой даты поиска (filter_start)
			startdate_weekday = filter_start.weekday()
			# определяем дату такого же дня недели, что и event_weekday, но на неделе, где идет поиск событий
			nearest_date = datetime.date(filter_start) - timedelta(days=startdate_weekday - event_weekday)
			print('nearest_date', nearest_date)
			# определяем количество дней между датами и проверяем, попали ли мы в правильную неделю
			if (nearest_date - event_start).days % (7 * interval) != 0:
				print('ku')
				# если мы попали в правильную неделю, то оставляем start_date, если нет - вычисляем нужную неделю и в качестве старта берем понедельник
				filter_start = (event_start + timedelta(weeks=interval)) - timedelta(days=event_weekday)
		# если событие повторяется по месяцам
		elif metadata['freq'] == 1:
			# считаем количество месяцев между стартовой датой поиска (filter_start) и датой начала события (event_start)
			month_count = (filter_start.year - event_start.year) * 12 + filter_start.month - event_start.month
			print('month_count', month_count)
			# если мы попали в правильный месяц, то оставляем start_date, если нет - вычисляем нужный месяц и в качестве старта берем 1-ое число
			if month_count % interval != 0:
				filter_start = (event_start + relativedelta(months=interval)).replace(day=1)
	elif event_start > datetime.date(filter_start) or event_start < datetime.date(filter_start) <= event_end:
		filter_start = event_start
	until = filter_end if not end_repeat or datetime.date(filter_end) <= end_repeat else end_repeat
	metadata['dtstart'] = filter_start
	metadata['until'] = until
	print('filter_start: ', filter_start)
	return list(rrule(**metadata))


