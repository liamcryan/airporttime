"""
The goal of this to to convert local time to utc time given a 3 character icao airport code.
data file here:
https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_best_known_so_far.csv

"""
import csv
import os
from datetime import datetime

import pytz
from timezonefinder import TimezoneFinder


class AirportTZ(object):
    def __init__(self, iata_code):
        self.iata_code = iata_code
        self.coordinates = None
        self.tz = self.get_tz()

    def get_tz(self):
        """ return the time zone string """
        # pk^iata_code^latitude^longitude^city_code^date_from (these are the column headers in the csv file)
        with open(os.path.join(os.path.abspath('.'), 'optd_por_best_known_so_far.csv'), 'rt', encoding='utf-8') as f:
            iata_code_index = 1
            latitude_index = 2
            longitude_index = 3
            reader = csv.reader(f, delimiter='^')
            for row in reader:
                if row[iata_code_index] != self.iata_code:
                    continue
                self.coordinates = (float(row[latitude_index]), float(row[longitude_index]))
                tf = TimezoneFinder()
                return tf.timezone_at(lng=self.coordinates[1], lat=self.coordinates[0])

    def to_utc(self, local_datetime: datetime) -> datetime:
        """ return the datetime converted to utc """
        local_tz = pytz.timezone(self.tz)  # this is the local timezone object
        dst = local_tz.localize(local_datetime).dst()  # this will return a timedelta with number 0 or 1 hour
        if dst.seconds == 0:
            return local_tz.localize(local_datetime, is_dst=False)
        return local_tz.localize(local_datetime, is_dst=True)


if __name__ == '__main__':
    import time
    st = time.time()
    a = AirportTZ('LAX')
    utc_time = a.to_utc(datetime.now())
    print(utc_time, datetime.utcnow())
    print('took: {}s'.format(time.time() - st))