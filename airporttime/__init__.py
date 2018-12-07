"""
The goal of this to to convert local time to utc time given a 3 character icao airport code.
data file here:
https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_best_known_so_far.csv

"""
import csv
from datetime import datetime
import os
import functools
import requests

import pytz
from timezonefinder import TimezoneFinder

LATITUDE_INDEX = 2
LONGITUDE_INDEX = 3
IATA_CODE_INDEX = 1
TIMEZONE_INDEX = 6

here = os.path.abspath(os.path.dirname(__file__))


@functools.lru_cache()
def get_airport_by_iata(iata_code: str):
    with open(os.path.join(os.path.abspath(here), 'optd_por_best_known_so_far.csv'), 'rt', encoding='utf-8') as f:
        iata_code_index = 1
        reader = csv.reader(f, delimiter='^')
        for row in reader:
            if row[iata_code_index] != iata_code:
                continue
            return row


class AirportDetails(object):
    def __init__(self, pk, iata_code, latitude, longitude, city_code, date_from, tz):
        self.pk = pk
        self.iata_code = iata_code
        self.latitude = latitude
        self.longitude = longitude
        self.city_code = city_code
        self.date_from = date_from
        self.tz = tz

    @classmethod
    def get_airport(cls, iata_code: str):
        """ return the time zone string """
        # pk^iata_code^latitude^longitude^city_code^date_from^timezone (these are the column headers in the csv file)
        row = [_ for _ in get_airport_by_iata(iata_code=iata_code)]
        return cls(*row[:-1])


class AirportTime(object):
    def __init__(self, iata_code: str):
        self.airport = AirportDetails.get_airport(iata_code=iata_code)

    def dst(self, dt: datetime, tz: pytz.tzfile) -> bool:
        dst = tz.localize(dt).dst()
        if dst.seconds == 0:
            return False
        return True

    def to_utc(self, loc_dt: datetime) -> datetime:
        """ returns a tz aware datetime converted to utc

        :param loc_dt: naive local datetime (no tz info)
        """

        local_tz = pytz.timezone(self.airport.tz)
        dst = self.dst(dt=loc_dt, tz=local_tz)
        utc_datetime = local_tz.localize(loc_dt, is_dst=dst).astimezone(pytz.utc)
        return utc_datetime

    def from_utc(self, utc_dt):
        """ returns a tz aware datetime converted from utc.
        :param utc: a naive / tz aware utc datetime (if not tz info given, utc assumed)
        """
        local_tz = pytz.timezone(self.airport.tz)
        return utc_dt.astimezone(local_tz)


def update_airports(**kwargs):
    url = 'https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_best_known_so_far.csv'
    r = requests.get(url, **kwargs)

    rows = r.text.split('\n')
    rows[0] += '^timezone'
    for i, row in enumerate(rows[1:]):
        if row == '':
            continue
        tf = TimezoneFinder()
        split_row = row.split('^')
        tz = tf.timezone_at(lng=float(split_row[LONGITUDE_INDEX]), lat=float(split_row[LATITUDE_INDEX]))
        if tz:
            rows[i+1] += '^' + tz + '^'
        else:
            rows[i+1] += '^'

    with open(os.path.join(os.path.abspath(here), 'optd_por_best_known_so_far.csv'), 'wt', encoding='utf-8') as f:
        f.write('\n'.join(rows))


if __name__ == '__main__':
    # update_airports()
    from datetime import timedelta
    a = AirportTime('LAX')
    local_datetime_dst = datetime(2018, 9, 1, 10, 30)
    utc_time_dst = a.to_utc(local_datetime_dst)
    assert local_datetime_dst == utc_time_dst.replace(tzinfo=None) - timedelta(days=0, seconds=60 * 60 * 7)
