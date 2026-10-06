"""Registered normalization and status rules; no file access or outcome reader."""
from datetime import date, timedelta
import math

def hhmm(value):
    value = str(value).strip() if value is not None else ''
    if not value.isascii() or not value.isdecimal():
        return None
    n = int(value)
    if n == 2400:
        return 0, 1
    if n // 100 < 24 and n % 100 < 60:
        return n // 100 * 60 + n % 100, 0
    return None

def cluster(source_year, flight_date, departure, key_valid=True):
    parsed = hhmm(departure)
    matching = flight_date + timedelta(days=parsed[1]) if parsed and key_valid else flight_date
    return source_year, matching - timedelta(days=matching.weekday())

def status(cancelled, diverted, delay):
    def number(v):
        if v is None or str(v).strip() == '':
            return None
        try:
            n = float(v)
        except (ValueError, TypeError):
            raise ValueError('invalid numeric status/delay') from None
        if not math.isfinite(n):
            raise ValueError('nonfinite numeric status/delay')
        return n
    a, b, d = number(cancelled), number(diverted), number(delay)
    if a not in (None, 0, 1) or b not in (None, 0, 1):
        raise ValueError('nonbinary status')
    if a == 1 or b == 1:
        return 0, 0
    if a == b == 0 and d is not None:
        return int(d < 15), 0
    return 0, 1

def fixtures():
    checks = {}
    for label, values, expected in [
        ('14.999', (0, 0, 14.999), (1, 0)), ('15', (0, 0, 15), (0, 0)),
        ('negative_delay', (0, 0, -10), (1, 0)),
        ('missing_delay', (0, 0, None), (0, 1)),
        ('missing_flag', (None, 0, 0), (0, 1)),
        ('cancel_precedence', (1, None, None), (0, 0)),
        ('divert_precedence', (None, 1, None), (0, 0)),
        ('both_failure_flags', (1, 1, None), (0, 0))]:
        assert status(*values) == expected
        checks[label] = True
    for label, values in [('nonbinary', (2, 0, 0)), ('invalid_delay', (1, 0, 'bad')),
                          ('infinite_delay', (0, 0, 'inf'))]:
        try:
            status(*values)
        except ValueError:
            checks[label] = True
        else:
            raise AssertionError(label)
    for v, expected in [('0', (0, 0)), ('2359', (1439, 0)), ('2400', (0, 1)),
                         ('1260', None), ('2401', None), ('-1', None),
                         ('12.5', None), ('', None), (None, None)]:
        assert hhmm(v) == expected
    checks['hhmm'] = True
    assert cluster(2023, date(2023, 1, 1), '2400') == cluster(2023, date(2023, 1, 2), '0000')
    checks['sunday_midnight_same_cluster'] = True
    assert cluster(2023, date(2023, 12, 31), '2400') == (2023, date(2024, 1, 1))
    assert cluster(2024, date(2024, 1, 1), '0000') == (2024, date(2024, 1, 1))
    checks['source_boundary_separate_cluster'] = True
    assert cluster(2023, date(2023, 1, 1), '2400', False) == (2023, date(2022, 12, 26))
    checks['invalid_key_uses_flightdate_week'] = True
    return checks
