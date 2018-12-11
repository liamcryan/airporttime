"""
    The goal is to convert a naive local time to utc time given a 3 character iata airport code.
"""
import csv
from datetime import datetime
import os
import functools
from typing import Optional, Dict

import pytz
import requests

DATA_SOURCE_URL = 'https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv'
DATA_SOURCE_FILE = os.path.join(os.path.abspath(os.path.abspath(os.path.dirname(__file__))), 'ori_por_public.csv')
LATITUDE_INDEX = 8
LONGITUDE_INDEX = 9
IATA_CODE_INDEX = 0
ICAO_CODE_INDEX = 1
TIMEZONE_INDEX = 31


@functools.lru_cache()
def get_airport_by_iata(iata_code: Optional[str] = None, icao_code: Optional[str] = None) -> Dict:
    """ Get the airport details for a given airport from the data source file.

    :param iata_code: a 3 character airport code
    :param icao_code: a 4 character airport code
    :returns: a dictionary representing the row
    """

    if iata_code:
        id_index = {'id': iata_code, 'index': IATA_CODE_INDEX}
    elif icao_code:
        id_index = {'id': icao_code, 'index': ICAO_CODE_INDEX}
    else:
        raise Exception('iata code or icao code must be provided.')

    with open(DATA_SOURCE_FILE, 'rt', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='^')
        headers = reader.__next__()
        for row in reader:
            if row[id_index['index']] != id_index['id']:
                continue
            return {headers[i]: v for i, v in enumerate(row)}


class AirportDetail(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    @classmethod
    def get_airport(cls, iata_code: Optional[str] = None, icao_code: Optional[str] = None):
        """ Get the details for a given airport.

        :param iata_code:  a 3 character airport code
        :param icao_code: a 4 character airport code
        :returns: instance of class
        """
        row = get_airport_by_iata(iata_code=iata_code, icao_code=icao_code)
        return cls(**row)


class AirportTime(object):
    def __init__(self, iata_code: Optional[str] = None, icao_code: Optional[str] = None):
        self.airport = AirportDetail.get_airport(iata_code=iata_code, icao_code=icao_code)

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

        local_tz = pytz.timezone(self.airport.__getattribute__('timezone'))
        dst = self._dst(dt=loc_dt, tz=local_tz)
        utc_datetime = local_tz.localize(loc_dt, is_dst=dst).astimezone(pytz.utc)
        return utc_datetime

    def from_utc(self, utc_dt: datetime):
        """ Convert a tz aware datetime in UTC back to local time.

        :param utc_dt: a naive / tz aware utc datetime (if not tz info given, utc assumed)
        :return: a tz aware datetime
        """
        local_tz = pytz.timezone(self.airport.__getattribute__('timezone'))
        return utc_dt.astimezone(local_tz)


def update_airports(**requests_kwargs):
    """ Update the ori_por_public.csv file directly from source.

    :param requests_kwargs: any kwargs you would like to pass to the requests.get method
            proxy={'http': '', 'https': ''}  <- might be useful if you are requesting within proxy server

    """
    r = requests.get(DATA_SOURCE_URL, **requests_kwargs)

    with open(DATA_SOURCE_FILE, 'wt', encoding='utf-8') as f:
        f.write(r.text)
