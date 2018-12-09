"""
    The goal is to convert a naive local time to utc time given a 3 character iata airport code.
"""
import csv
from datetime import datetime
import os
import functools
import requests

import pytz
from timezonefinder import TimezoneFinder

DATA_SOURCE_URL = 'https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_best_known_so_far.csv'
LATITUDE_INDEX = 2
LONGITUDE_INDEX = 3
IATA_CODE_INDEX = 1
TIMEZONE_INDEX = 6

here = os.path.abspath(os.path.dirname(__file__))


@functools.lru_cache()
def get_airport_by_iata(iata_code: str) -> str:
    """ Get the airport details for a given airport from the data source file.

    :param iata_code: a 3 character airport code
    :returns: a row of text
    """
    if len(iata_code) == 4:
        raise Exception('iata code must be provided.')

    with open(os.path.join(os.path.abspath(here), 'optd_por_best_known_so_far.csv'), 'rt', encoding='utf-8') as f:
        iata_code_index = 1
        reader = csv.reader(f, delimiter='^')
        for row in reader:
            if row[iata_code_index] != iata_code:
                continue
            return row


class AirportDetail(object):
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
        """ Get the details for a given airport.

        :param iata_code:  a three character airport code
        :returns: instance of class
        """
        row = [_ for _ in get_airport_by_iata(iata_code=iata_code)]
        return cls(*row)


class AirportTime(object):
    def __init__(self, iata_code: str):
        self.airport = AirportDetail.get_airport(iata_code=iata_code)

    @staticmethod
    def _dst(dt: datetime, tz: pytz.tzfile) -> bool:
        """ Find out if the provided naive datetime and time zone are in daylight savings time or not.

        :param dt: the date you are referencing
        :param tz: the time zone you are referencing
        :returns: bool
        """
        dst = tz.localize(dt).dst()
        if dst.seconds == 0:
            return False
        return True

    def to_utc(self, loc_dt: datetime) -> datetime:
        """ Convert a datetime from local time to UTC.

        :param loc_dt: naive local datetime
        :return: a tz aware datetime
        """
        if loc_dt.tzinfo:
            raise Exception('Must provide a naive datetime (no tzinfo)')

        local_tz = pytz.timezone(self.airport.tz)
        dst = self._dst(dt=loc_dt, tz=local_tz)
        utc_datetime = local_tz.localize(loc_dt, is_dst=dst).astimezone(pytz.utc)
        return utc_datetime

    def from_utc(self, utc_dt: datetime):
        """ Convert a tz aware datetime in UTC back to local time.

        :param utc_dt: a naive / tz aware utc datetime (if not tz info given, utc assumed)
        :return: a tz aware datetime
        """
        local_tz = pytz.timezone(self.airport.tz)
        return utc_dt.astimezone(local_tz)


def update_airports(**requests_kwargs):
    """ Update the optd_por_best_known_so_far.csv file directly from source.

    :param requests_kwargs: any kwargs you would like to pass to the requests.get method
            proxy={'http': '', 'https': ''}  <- might be useful if you are requesting within proxy server

    """
    r = requests.get(DATA_SOURCE_URL, **requests_kwargs)

    rows = r.text.split('\n')
    rows[0] += '^timezone'
    for i, row in enumerate(rows[1:]):
        if row == '':
            continue
        tf = TimezoneFinder()
        split_row = row.split('^')
        tz = tf.timezone_at(lng=float(split_row[LONGITUDE_INDEX]), lat=float(split_row[LATITUDE_INDEX]))
        if tz:
            rows[i+1] += '^' + tz

    with open(os.path.join(os.path.abspath(here), 'optd_por_best_known_so_far.csv'), 'wt', encoding='utf-8') as f:
        f.write('\n'.join(rows))
if __name__ == '__main__':
    AirportTime('ORD')
    AirportTime('ORD')
    AirportTime('JFK')

    cache_info = get_airport_by_iata.cache_info()
    print('ok')