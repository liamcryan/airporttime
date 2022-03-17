import os
import unittest
from datetime import timedelta, datetime

import pytest
import pytz

from stationtz import Airport, get_airport_details, AirportDetail, MANUAL_STATION_SOURCE_FILE


class StationTZTestCase(unittest.TestCase):
    loc_time_dst_naive = datetime(2018, 9, 1, 10, 30)
    loc_time_not_dst_naive = datetime(2018, 12, 3, 10, 30)
    iata_code = 'LAX'
    icao_code = 'KLAX'
    tz = 'America/Los_Angeles'

    def test_airport_tz(self):
        self.assertEqual(AirportDetail.get_airport(iata_code=self.iata_code).__getattribute__('timezone'), self.tz)

    def test_is_dst(self):
        self.assertTrue(
            Airport._dst(dt=self.loc_time_dst_naive, tz=pytz.timezone(self.tz)))

    def test_is_not_dst(self):
        assert Airport._dst(dt=self.loc_time_not_dst_naive, tz=pytz.timezone(self.tz)) is False

    def test_to_utc_daylight_savings_time(self):
        a = Airport(iata_code=self.iata_code)
        local_datetime_dst = self.loc_time_dst_naive
        utc_time_dst = a.to_utc(local_datetime_dst)
        self.assertEqual(local_datetime_dst, utc_time_dst.replace(tzinfo=None) - timedelta(days=0, seconds=60 * 60 * 7))

    def test_to_utc_not_daylight_savings_time(self):
        a = Airport(iata_code=self.iata_code)
        local_datetime_no_dst = self.loc_time_not_dst_naive
        utc_time_no_dst = a.to_utc(local_datetime_no_dst)
        self.assertEqual(local_datetime_no_dst,
                         utc_time_no_dst.replace(tzinfo=None) - timedelta(days=0, seconds=60 * 60 * 8))

    def test_from_utc(self):
        a = Airport(iata_code=self.iata_code)
        utc_time = a.to_utc(self.loc_time_dst_naive)
        self.assertEqual(a.from_utc(utc_time).replace(tzinfo=None), self.loc_time_dst_naive)

    def test_icao_iata(self):
        a = Airport(iata_code=self.iata_code)
        b = Airport(icao_code=self.icao_code)
        self.assertEqual(a.airport.__dict__, b.airport.__dict__)


class CacheTestCase(unittest.TestCase):
    iata1 = 'ORD'
    iata2 = 'JFK'

    def test_lru_cache(self):
        get_airport_details.cache_clear()

        Airport(iata_code=self.iata1)
        Airport(iata_code=self.iata1)
        Airport(iata_code=self.iata2)

        cache_info = get_airport_details.cache_info()

        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 2)
        self.assertEqual(cache_info.currsize, 2)


@pytest.fixture(scope="function")
def create_wxyz():
    with open(MANUAL_STATION_SOURCE_FILE, "wt") as f:
        f.write("iata_code,icao_code,timezone\n,WXYZ,America/New_York")
    yield
    os.remove(MANUAL_STATION_SOURCE_FILE)


def test_manual_station(create_wxyz):
    wxyz = Airport(icao_code="WXYZ")


def test_missing_station():
    wxyz = Airport(icao_code="WXYZ")
