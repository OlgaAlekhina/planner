from .services import get_dates
import datetime

def test_daily_event_int1():
	assert get_dates(
		metadata = {'freq': 3, 'interval': 1, 'byweekday': None, 'bymonthday': None, 'bymonth': None, 'byweekno': None},
		filter_start = '2025-01-28',
		filter_end = '2025-02-10',
		event_start = datetime.date(2025, 1, 28),
		event_end = datetime.date(2025, 1, 28),
		end_repeat = datetime.date(2025, 3, 1)
	) == [datetime.datetime(2025, 1, 28, 0, 0), datetime.datetime(2025, 1, 29, 0, 0), datetime.datetime(2025, 1, 30, 0, 0),
		  datetime.datetime(2025, 1, 31, 0, 0), datetime.datetime(2025, 2, 1, 0, 0), datetime.datetime(2025, 2, 2, 0, 0),
		  datetime.datetime(2025, 2, 3, 0, 0), datetime.datetime(2025, 2, 4, 0, 0), datetime.datetime(2025, 2, 5, 0, 0),
		  datetime.datetime(2025, 2, 6, 0, 0), datetime.datetime(2025, 2, 7, 0, 0), datetime.datetime(2025, 2, 8, 0, 0),
		  datetime.datetime(2025, 2, 9, 0, 0), datetime.datetime(2025, 2, 10, 0, 0)]

def test_daily_event_int5():
	assert get_dates(
		metadata = {'freq': 3, 'interval': 5, 'byweekday': None, 'bymonthday': None, 'bymonth': None, 'byweekno': None},
		filter_start = '2025-01-28',
		filter_end = '2025-02-10',
		event_start = datetime.date(2025, 1, 28),
		event_end = datetime.date(2025, 1, 28),
		end_repeat = datetime.date(2025, 3, 1)
	) == [datetime.datetime(2025, 1, 28, 0, 0), datetime.datetime(2025, 2, 2, 0, 0),
		  datetime.datetime(2025, 2, 7, 0, 0)]

def test_daily_event_int10_dur3():
	assert get_dates(
		metadata = {'freq': 3, 'interval': 10, 'byweekday': None, 'bymonthday': None, 'bymonth': None, 'byweekno': None},
		filter_start = '2025-02-28',
		filter_end = '2025-06-10',
		event_start = datetime.date(2025, 1, 28),
		event_end = datetime.date(2025, 1, 30),
		end_repeat = datetime.date(2025, 5, 1)
	) == [datetime.datetime(2025, 2, 27, 0, 0), datetime.datetime(2025, 3, 9, 0, 0),
		  datetime.datetime(2025, 3, 19, 0, 0), datetime.datetime(2025, 3, 29, 0, 0),
		  datetime.datetime(2025, 4, 8, 0, 0), datetime.datetime(2025, 4, 18, 0, 0),
		  datetime.datetime(2025, 4, 28, 0, 0)]

def test_weekly_event_int1():
	assert get_dates(
		metadata = {'freq': 2, 'interval': 1, 'byweekday': [1, 5], 'bymonthday': None, 'bymonth': None, 'byweekno': None},
		filter_start = '2025-02-28',
		filter_end = '2025-04-10',
		event_start = datetime.date(2025, 3, 15),
		event_end = datetime.date(2025, 3, 15),
		end_repeat = datetime.date(2025, 8, 14)
	) == [datetime.datetime(2025, 3, 15, 0, 0), datetime.datetime(2025, 3, 18, 0, 0),
		  datetime.datetime(2025, 3, 22, 0, 0), datetime.datetime(2025, 3, 25, 0, 0),
		  datetime.datetime(2025, 3, 29, 0, 0), datetime.datetime(2025, 4, 1, 0, 0),
		  datetime.datetime(2025, 4, 5, 0, 0), datetime.datetime(2025, 4, 8, 0, 0)]

def test_weekly_event_int1_per3():
	assert get_dates(
		metadata = {'freq': 2, 'interval': 1, 'byweekday': [1, 5], 'bymonthday': None, 'bymonth': None, 'byweekno': None},
		filter_start = '2025-02-28',
		filter_end = '2025-04-10',
		event_start = datetime.date(2025, 3, 15),
		event_end = datetime.date(2025, 3, 15),
		end_repeat = datetime.date(2025, 8, 14)
	) == [datetime.datetime(2025, 3, 15, 0, 0), datetime.datetime(2025, 3, 18, 0, 0),
		  datetime.datetime(2025, 3, 22, 0, 0), datetime.datetime(2025, 3, 25, 0, 0),
		  datetime.datetime(2025, 3, 29, 0, 0), datetime.datetime(2025, 4, 1, 0, 0),
		  datetime.datetime(2025, 4, 5, 0, 0), datetime.datetime(2025, 4, 8, 0, 0)]

def test_weekly_event_int2_per3():
	assert get_dates(
		metadata = {'freq': 2, 'interval': 2, 'byweekday': [1, 5], 'bymonthday': None, 'bymonth': None, 'byweekno': None},
		filter_start = '2025-03-17',
		filter_end = '2025-04-15',
		event_start = datetime.date(2025, 3, 16),
		event_end = datetime.date(2025, 3, 18),
		end_repeat = datetime.date(2025, 8, 14)
	) == [datetime.datetime(2025, 3, 25, 0, 0), datetime.datetime(2025, 3, 29, 0, 0),
		  datetime.datetime(2025, 4, 8, 0, 0), datetime.datetime(2025, 4, 12, 0, 0)]