import unittest
from datetime import timedelta, datetime

from airporttime import AirportTime, get_airport_by_iata


class DSTTestCase(unittest.TestCase):

    def test_to_utc_daylight_savings_time(self):
        a = AirportTime('LAX')
        local_datetime_dst = datetime(2018, 9, 1, 10, 30)
        utc_time_dst = a.to_utc(local_datetime_dst)
        self.assertEqual(local_datetime_dst, utc_time_dst.replace(tzinfo=None) - timedelta(days=0, seconds=60 * 60 * 7))

    def test_to_utc_not_daylight_savings_time(self):
        a = AirportTime('LAX')
        local_datetime_no_dst = datetime(2018, 12, 3, 10, 30)
        utc_time_no_dst = a.to_utc(local_datetime_no_dst)
        self.assertEqual(local_datetime_no_dst,
                         utc_time_no_dst.replace(tzinfo=None) - timedelta(days=0, seconds=60 * 60 * 8))


class CacheTestCase(unittest.TestCase):

    def test_lru_cache(self):
        AirportTime('LAX')
        AirportTime('LAX')
        AirportTime('JFK')

        cache_info = get_airport_by_iata.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 2)
        self.assertEqual(cache_info.currsize, 2)
