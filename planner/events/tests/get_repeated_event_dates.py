from events.services import get_dates
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

def test_weekly_event_int1_dur3():
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

def test_weekly_event_int2_dur3():
	assert get_dates(
		metadata = {'freq': 2, 'interval': 2, 'byweekday': [1, 5], 'bymonthday': None, 'bymonth': None, 'byweekno': None},
		filter_start = '2025-03-17',
		filter_end = '2025-04-15',
		event_start = datetime.date(2025, 3, 16),
		event_end = datetime.date(2025, 3, 18),
		end_repeat = datetime.date(2025, 8, 14)
	) == [datetime.datetime(2025, 3, 25, 0, 0), datetime.datetime(2025, 3, 29, 0, 0),
		  datetime.datetime(2025, 4, 8, 0, 0), datetime.datetime(2025, 4, 12, 0, 0)]

def test_monthly_event_int1():
	assert get_dates(
		metadata = {'freq': 1, 'interval': 1, 'byweekday': None, 'bymonthday': [15], 'bymonth': None, 'byweekno': None},
		filter_start = '2025-04-21',
		filter_end = '2025-08-21',
		event_start = datetime.date(2025, 4, 15),
		event_end = datetime.date(2025, 4, 15),
		end_repeat = None
	) == [datetime.datetime(2025, 5, 15, 0, 0), datetime.datetime(2025, 6, 15, 0, 0),
		  datetime.datetime(2025, 7, 15, 0, 0), datetime.datetime(2025, 8, 15, 0, 0)]

def test_monthly_event_int3_dur3():
	assert get_dates(
		metadata = {'freq': 1, 'interval': 3, 'byweekday': None, 'bymonthday': [15], 'bymonth': None, 'byweekno': None},
		filter_start = '2025-05-21',
		filter_end = '2026-09-21',
		event_start = datetime.date(2025, 4, 15),
		event_end = datetime.date(2025, 4, 17),
		end_repeat = None
	) == [datetime.datetime(2025, 7, 15, 0, 0), datetime.datetime(2025, 10, 15, 0, 0),
		  datetime.datetime(2026, 1, 15, 0, 0), datetime.datetime(2026, 4, 15, 0, 0),
		  datetime.datetime(2026, 7, 15, 0, 0)]

def test_monthly_event_int2_dur3():
	assert get_dates(
		metadata = {'freq': 1, 'interval': 2, 'byweekday': None, 'bymonthday': [15], 'bymonth': None, 'byweekno': None},
		filter_start = '2025-04-13',
		filter_end = '2026-09-21',
		event_start = datetime.date(2025, 4, 12),
		event_end = datetime.date(2025, 4, 14),
		end_repeat = None
	) == [datetime.datetime(2025, 4, 15, 0, 0), datetime.datetime(2025, 6, 15, 0, 0),
		  datetime.datetime(2025, 8, 15, 0, 0), datetime.datetime(2025, 10, 15, 0, 0),
		  datetime.datetime(2025, 12, 15, 0, 0), datetime.datetime(2026, 2, 15, 0, 0),
		  datetime.datetime(2026, 4, 15, 0, 0), datetime.datetime(2026, 6, 15, 0, 0),
		  datetime.datetime(2026, 8, 15, 0, 0)]

def test_yearly_event_int1():
	assert get_dates(
		metadata = {'freq': 0, 'interval': 1, 'byweekday': None, 'bymonthday': [9], 'bymonth': 5, 'byweekno': None},
		filter_start = '2025-03-31',
		filter_end = '2026-09-21',
		event_start = datetime.date(2025, 5, 9),
		event_end = datetime.date(2025, 5, 9),
		end_repeat = None
	) == [datetime.datetime(2025, 5, 9, 0, 0), datetime.datetime(2026, 5, 9, 0, 0)]

def test_yearly_event_int2_dur3():
	assert get_dates(
		metadata = {'freq': 0, 'interval': 2, 'byweekday': None, 'bymonthday': [30], 'bymonth': 12, 'byweekno': None},
		filter_start = '2025-12-31',
		filter_end = '2036-09-21',
		event_start = datetime.date(2025, 12, 30),
		event_end = datetime.date(2026, 1, 1),
		end_repeat = datetime.date(2033, 3, 20)
	) == [datetime.datetime(2025, 12, 30, 0, 0), datetime.datetime(2027, 12, 30, 0, 0),
		  datetime.datetime(2029, 12, 30, 0, 0), datetime.datetime(2031, 12, 30, 0, 0)]