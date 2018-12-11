"""
Calculate the Bible Overview readings for a given range of dates. 
Assumptions:

* Reading starts January 1
* No readings on Sunday
* List of readings in Bible-Overview.json
"""

import json, os, sys
from datetime import date, timedelta
from pathlib import Path
from biblicity_net import config, PATH

RESOURCES_PATH = os.path.join(os.path.dirname(PATH), 'resources')
with (Path(RESOURCES_PATH) / 'Bible-Overview.json').open() as f:
    READINGS_LIST = json.load(f)


def range_readings(date1, date2=None):
    date2 = date2 or date1
    date_range = [date1 + timedelta(i) for i in range(0, (date2 - date1).days + 1)]
    return [(d, date_reading(d)) for d in date_range]


def date_reading(date1):
    i = reading_index(date1)
    if i is not None:
        if i < len(READINGS_LIST):
            return READINGS_LIST[i]


def reading_index(date1):
    """for a given datetime date, return the reading index for that date
    * no Sundays
    """
    jan1 = date(date1.year, 1, 1)
    dates = reading_dates(jan1.year)
    if date1 in dates:
        return dates.index(date1)


def reading_dates(year):
    jan1 = date(year, 1, 1)
    return [
        d
        for d in [jan1 + timedelta(n) for n in range(0, (date(year + 1, 1, 1) - jan1).days)]
        if d.timetuple().tm_wday != 6
    ]
