import unittest
from datetime import timedelta, datetime

import pytz

from airporttime import AirportTime, get_airport_by_iata, AirportDetail


class AirportTimeTestCase(unittest.TestCase):
    loc_time_dst_naive = datetime(2018, 9, 1, 10, 30)
    loc_time_not_dst_naive = datetime(2018, 12, 3, 10, 30)
    iata_code = 'LAX'
    icao_code = 'KLAX'
    tz = 'America/Los_Angeles'

    def test_airport_tz(self):
        self.assertEqual(AirportDetail.get_airport(iata_code=self.iata_code).__getattribute__('timezone'), self.tz)

    def test_is_dst(self):
        self.assertTrue(
            AirportTime._dst(dt=self.loc_time_dst_naive, tz=pytz.timezone(self.tz)))

    def test_is_not_dst(self):
        assert AirportTime._dst(dt=self.loc_time_not_dst_naive, tz=pytz.timezone(self.tz)) is False

    def test_to_utc_daylight_savings_time(self):
        a = AirportTime(self.iata_code)
        local_datetime_dst = self.loc_time_dst_naive
        utc_time_dst = a.to_utc(local_datetime_dst)
        self.assertEqual(local_datetime_dst, utc_time_dst.replace(tzinfo=None) - timedelta(days=0, seconds=60 * 60 * 7))

    def test_to_utc_not_daylight_savings_time(self):
        a = AirportTime(self.iata_code)
        local_datetime_no_dst = self.loc_time_not_dst_naive
        utc_time_no_dst = a.to_utc(local_datetime_no_dst)
        self.assertEqual(local_datetime_no_dst,
                         utc_time_no_dst.replace(tzinfo=None) - timedelta(days=0, seconds=60 * 60 * 8))

    def test_from_utc(self):
        a = AirportTime(self.iata_code)
        utc_time = a.to_utc(self.loc_time_dst_naive)
        self.assertEqual(a.from_utc(utc_time).replace(tzinfo=None), self.loc_time_dst_naive)

    def test_icao_iata(self):
        a = AirportTime(iata_code=self.iata_code)
        b = AirportTime(icao_code=self.icao_code)
        self.assertEqual(a.airport.__dict__, b.airport.__dict__)


class CacheTestCase(unittest.TestCase):
    iata1 = 'ORD'
    iata2 = 'JFK'

    def test_lru_cache(self):
        get_airport_by_iata.cache_clear()

        AirportTime(self.iata1)
        AirportTime(self.iata1)
        AirportTime(self.iata2)

        cache_info = get_airport_by_iata.cache_info()

        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 2)
        self.assertEqual(cache_info.currsize, 2)
