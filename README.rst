===========
airporttime
===========

Convert local time to utc time by airport or vise-versa.

This works thanks to opentraveldata.  The data source for converting iata code to coordinates is here:
https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_best_known_so_far.csv

Once the coordinates are found, the python library timezonefinder is able to calculate the time zone.  The library
pytz is used for datetime conversions.


Usage
_____

Here is the usage::

    import airporttime

    apt = airporttime.AirportTime(iata_code='ORD')

    # convert your naive local time to utc
    naive_loc_time = datetime(2019, 1, 1, 10, 30)

    tz_aware_utc_time = apt.to_utc(naive_loc_time)

    # convert your tz aware back to local time if you want to
    tz_aware_loc_time = apt.from_utc(tz_aware_utc_time)

    # you can make your tz_aware times naive (this can be helpful and is part of the datetime library)
    tz_aware_utc_time.replace(tzinfo=None)
    tz_aware_loc_time.replace(tzinfo=None)


Features
________

This library stores the iata/coordinate info in a csv file.  When you ask for a iata airport station, this file
is opened and searched until the station is found.

If you are converting a lot of station times from local to utc for example, it is beneficial for speed to
open this file as few times as possible.  functools.lru_cache is used so that if you convert a local datetime at
'JFK' more than once, the results will be cached and the file opened only once.

An alternate approach is to load all the data in memory.


Improvements
____________

It would be nice to update the csv file automatically::

    airporttime.update()

During this update process, timezonefinder could be run on each iata code and stored in the csv as well.  This way
the time zone doesn't need to be looked up for each call.
