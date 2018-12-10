===========
airporttime
===========

Convert local time to utc time by airport or vise-versa.

This works thanks to data from opentraveldata.  The data source is here:
https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv


Usage
_____

Here is the usage::

    # import the library
    import airporttime

    # create an instance of AirportTime
    apt = airporttime.AirportTime(iata_code='ORD')

    # convert your naive (or tz aware) local time to utc
    naive_loc_time = datetime(2019, 1, 1, 10, 30)
    tz_aware_utc_time = apt.to_utc(naive_loc_time)

    # convert your tz aware back to local time if you want to
    tz_aware_loc_time = apt.from_utc(tz_aware_utc_time)

    # you can make your tz_aware times naive (this can be helpful and is part of the datetime library)
    tz_aware_utc_time.replace(tzinfo=None)
    tz_aware_loc_time.replace(tzinfo=None)

    # if for some reason you would like to update the data file, you can use (but it takes a while):
    airporttime.update()
