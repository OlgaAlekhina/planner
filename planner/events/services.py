from datetime import datetime, timedelta
from dateutil.rrule import *
from dateutil.parser import *
from dateutil.relativedelta import relativedelta


def get_dates(
		metadata: dict,
		filter_start: str,
		filter_end: str,
		event_start: datetime.date,
		event_end: datetime.date,
		end_repeat: datetime.date
	) -> list[datetime]:
	""" Функция для вычисления списка дат для повторяющихся событий с помощью библиотеки rrule """
	saved_args = {**locals()}
	print("saved_args is", saved_args)
	filter_start = parse(filter_start)
	filter_end = parse(filter_end)
	# считаем продолжительность события (начиная от 1)
	duration = (event_end - event_start).days + 1
	interval = metadata['interval']

	# вычисляем дату начала для периодических событий
	if interval > 1 and event_end < datetime.date(filter_start):
		print('1')
		# если событие повторяется по дням
		if metadata['freq'] == 3:
			# вычисляем количество дней между стартовой датой поиска (filter_start) и датой начала события (event_start)
			days_count = (datetime.date(filter_start) - event_start).days
			mod = days_count % interval
			# определяем новую дату начала повторений
			if duration <= mod:
				filter_start += timedelta(days=interval - mod)
			else:
				filter_start -= timedelta(days=mod)

		# если событие повторяется по неделям
		elif metadata['freq'] == 2:
			# сдвигаем дату начала периодического события, если оно длится более 1 дня
			filter_start -= timedelta(days=duration-1)
			# определяем день недели даты начала события (event_start)
			event_weekday = event_start.weekday()
			# определяем день недели стартовой даты поиска (filter_start)
			startdate_weekday = filter_start.weekday()
			# определяем дату такого же дня недели, что и event_weekday, но на той неделе, где идет поиск событий
			nearest_date = datetime.date(filter_start) - timedelta(days=startdate_weekday - event_weekday)
			# определяем количество дней между датами и проверяем, попали ли мы в правильную неделю
			week_count = (nearest_date - event_start).days / 7
			if week_count % interval > 0:
				# если мы попали в правильную неделю, то оставляем filter_start, если нет - вычисляем нужную неделю и в
				# качестве старта берем понедельник
				filter_start += timedelta(weeks=interval - week_count % interval) - timedelta(days=startdate_weekday)

		# если событие повторяется по месяцам
		elif metadata['freq'] == 1:
			# считаем количество месяцев между стартовой датой поиска (filter_start) и датой начала события (event_start)
			month_count = (filter_start.year - event_start.year) * 12 + filter_start.month - event_start.month
			# если мы попали в правильный месяц, то оставляем filter_start, если нет - вычисляем нужный месяц и в качестве старта берем 1-ое число
			if month_count % interval != 0:
				filter_start += relativedelta(months=interval - month_count % interval)
				filter_start = filter_start.replace(day=1)

		# если событие повторяется по годам (metadata['freq'] == 0)
		else:
			# считаем количество лет между стартовой датой поиска (filter_start) и датой начала события (event_start)
			year_count = filter_start.year - event_start.year
			# если мы попали в правильный год, то оставляем filter_start, если нет - вычисляем нужный год и в качестве старта берем 1 января
			if year_count % interval != 0:
				filter_start += relativedelta(years=interval - year_count % interval)
				filter_start = filter_start.replace(day=1, month=1)

	# если событие начинается позже, чем начало поиска, или начало поиска совпадает или раньше даты окончания события, то стартом будет дата начала события
	elif event_start > datetime.date(filter_start) or event_start <= datetime.date(filter_start) <= event_end:
		print('2')
		filter_start = event_start

	# сдвигаем дату начала периодического события, если оно длится более 1 дня
	else:
		print('3')
		filter_start -= timedelta(days=duration - 1)

	# определяем конец повторений
	until = filter_end if not end_repeat or datetime.date(filter_end) <= end_repeat else end_repeat
	metadata['dtstart'] = filter_start
	metadata['until'] = until
	print('filter_start: ', filter_start)
	return list(rrule(**metadata))


