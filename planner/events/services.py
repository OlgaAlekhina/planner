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
	"""
	Функция для вычисления списка дат для повторяющихся событий с помощью библиотеки rrule.
	Ее основная задача - правильно определить даты начала (filter_start) и конца (until) повторов, которые надо передать
	в функцию rrule() вместе с метаданными события, описывающими паттерн повторений.
	"""

	filter_start = parse(filter_start)
	filter_end = parse(filter_end)
	interval = metadata['interval']

	# считаем продолжительность события (начиная от 1 дня)
	duration = (event_end - event_start).days + 1

	# если стартовая дата поиска меньше даты окончания события
	if datetime.date(filter_start) <= event_end:
		filter_start = event_start

	else:
		# сдвигаем дату начала периодического события, если оно длится более 1 дня
		filter_start -= timedelta(days=duration - 1)

		# вычисляем дату начала для периодических событий для разных паттернов
		if interval > 1:
			# если событие повторяется по дням
			if metadata['freq'] == 3:
				# вычисляем количество дней между стартовой датой поиска (filter_start) и датой начала события (event_start)
				days_count = (datetime.date(filter_start) - event_start).days
				# если не попали в правильный день, то определяем новую дату начала повторений
				if days_count % interval > 0:
					filter_start += timedelta(days=interval - days_count % interval)

			# если событие повторяется по неделям
			elif metadata['freq'] == 2:
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
				# если мы попали в правильный месяц, то оставляем filter_start, если нет - вычисляем нужный месяц и в
				# качестве старта берем 1-ое число
				if month_count % interval != 0:
					filter_start += relativedelta(months=interval - month_count % interval)
					filter_start = filter_start.replace(day=1)

			# если событие повторяется по годам (metadata['freq'] == 0)
			else:
				# считаем количество лет между стартовой датой поиска (filter_start) и датой начала события (event_start)
				year_count = filter_start.year - event_start.year
				# если мы попали в правильный год, то оставляем filter_start, если нет - вычисляем нужный год и в
				# качестве старта берем 1 января
				if year_count % interval != 0:
					filter_start += relativedelta(years=interval - year_count % interval)
					filter_start = filter_start.replace(day=1, month=1)

	# определяем конец повторений
	until = filter_end if not end_repeat or datetime.date(filter_end) <= end_repeat else end_repeat

	metadata['dtstart'] = filter_start
	metadata['until'] = until
	print('filter_start: ', filter_start)
	return list(rrule(**metadata))


