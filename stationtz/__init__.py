"""
    The goal is to convert a naive local time to utc time given a 3 character iata airport code.
"""
import csv
import datetime
import os
import logging
import functools
from typing import Optional, Dict, List

import pytz

logging.getLogger(__name__).addHandler(logging.NullHandler())

DATA_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
AIRPORT_SOURCE_FILE = os.path.join(DATA_DIRECTORY, "ori_por_public.csv")
MANUAL_STATION_SOURCE_FILE = os.path.join(DATA_DIRECTORY, "manual_airports.csv")
LATITUDE_INDEX = 8
LONGITUDE_INDEX = 9
IATA_CODE_INDEX = 0
ICAO_CODE_INDEX = 1
TIMEZONE_INDEX = 31


class StationNotFound(Exception):
    pass


@functools.lru_cache()
def get_airport_details(*, iata_code: Optional[str] = None, icao_code: Optional[str] = None) -> Optional[Dict]:
    """ Get the airport details for a given airport from the data source file.

    :param iata_code: a 3 character airport code
    :param icao_code: a 4 character airport code
    :returns: a dictionary representing the row
    """

    if iata_code:
        id_index = {'id': iata_code.upper(), 'index': IATA_CODE_INDEX}
    elif icao_code:
        id_index = {'id': icao_code.upper(), 'index': ICAO_CODE_INDEX}
    else:
        raise Exception('iata code or icao code must be provided.')

    def find_airport_in_csv(file, delimiter):
        with open(file, 'rt', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            headers = reader.__next__()
            for row in reader:
                if row[id_index['index']] != id_index['id']:
                    continue
                return {headers[i]: v for i, v in enumerate(row)}

    try:
        detail = find_airport_in_csv(AIRPORT_SOURCE_FILE, delimiter="^")
    except FileNotFoundError as e:
        raise Exception("Airport file not found, please use `python -m stationtz update_airports`\n"
                        f"{e}")
    if not detail:
        try:
            detail = find_airport_in_csv(MANUAL_STATION_SOURCE_FILE, delimiter=",")
        except FileNotFoundError:
            logging.warning(
                "Manual airports not set.  To do so use, `python -m stationtz create_airports /path/to/manual/file.csv`")

    return detail


class AirportDetail(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    @classmethod
    def get_airport(cls, *, iata_code: Optional[str] = None, icao_code: Optional[str] = None):
        """ Get the details for a given airport.

        :param iata_code:  a 3 character airport code
        :param icao_code: a 4 character airport code
        :returns: instance of class
        """
        row = get_airport_details(iata_code=iata_code, icao_code=icao_code)
        if not row:
            raise StationNotFound(f"Sorry, the airport station was not found.\n"
                                  f"Please manually create the station using `python -m stationtz create_airports ")
        return cls(**row)


class Airport(object):
    def __init__(self, *, iata_code: Optional[str] = None, icao_code: Optional[str] = None):
        if iata_code and len(iata_code) != 3:
            if len(iata_code) == 4:
                raise Exception(f"The code you entered is 4 characters.\n"
                                f"iata code should be 3 characters, while icao codes should be 4")
            raise Exception("Please enter a 3 character iata code.")
        if icao_code and len(icao_code) != 4:
            if len(icao_code) == 3:
                raise Exception(f"The code you entered is 3 characters.\n"
                                f"icao code should be 4 characters, while iata codes should be 3")
            raise Exception("Please enter a 4 character icao code.")

        self.airport = AirportDetail.get_airport(iata_code=iata_code, icao_code=icao_code)

    @staticmethod
    def _dst(dt: datetime.datetime, tz: pytz.tzfile) -> bool:
        """ Find out if the provided naive datetime and time zone are in daylight savings time or not.

        :param dt: the date you are referencing
        :param tz: the time zone you are referencing
        :returns: bool
        """
        dst = tz.localize(dt).dst()
        if dst.seconds == 0:
            return False
        return True

    def to_utc(self, loc_dt: datetime.datetime) -> datetime.datetime:
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

    def from_utc(self, utc_dt: datetime.datetime):
        """ Convert a tz aware datetime in UTC back to local time.

        :param utc_dt: a naive / tz aware utc datetime (if not tz info given, utc assumed)
        :return: a tz aware datetime
        """
        local_tz = pytz.timezone(self.airport.__getattribute__('timezone'))
        return utc_dt.astimezone(local_tz)