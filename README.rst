===========
airporttime
===========

Convert local time to utc time by airport or vise-versa.

This works thanks to data from opentraveldata.  The data source is here:
https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv


Usage
_____

Here is the usage::

    >>> # import the library
    >>> import airporttime

    >>> # we are also going to use the datetime library
    >>> from datetime import datetime

    >>> # create an instance of AirportTime at 'ORD'
    >>> apt = airporttime.AirportTime(iata_code='ORD')

    >>> # ** side note ** the apt object contains one attribute, basically an instance of a row of data
    >>> print(apt.airport.__dict__)
    {'iata_code': 'ORD', 'icao_code': 'KORD', 'faa_code': 'ORD', 'is_geonames': 'Y', 'geoname_id': '4887479', 'envelope_id': '', 'name': "Chicago O'Hare International Airport", 'asciiname': "Chicago O'Hare International Airport", 'latitude': '41.978603', 'longitude': '-87.904842', 'fclass': 'S', 'fcode': 'AIRP', 'page_rank': '0.4871606262308594', 'date_from': '', 'date_until': '', 'comment': '', 'country_code': 'US', 'cc2': '', 'country_name': 'United States', 'continent_name': 'North America', 'adm1_code': 'IL', 'adm1_name_utf': 'Illinois', 'adm1_name_ascii': 'Illinois', 'adm2_code': '031', 'adm2_name_utf': 'Cook County', 'adm2_name_ascii': 'Cook County', 'adm3_code': '14000', 'adm4_code': '', 'population': '0', 'elevation': '201', 'gtopo30': '202', 'timezone': 'America/Chicago', 'gmt_offset': '-6.0', 'dst_offset': '-5.0', 'raw_offset': '-6.0', 'moddate': '2018-03-29', 'city_code_list': 'CHI', 'city_name_list': 'Chicago', 'city_detail_list': 'CHI|4887398|Chicago|Chicago', 'tvl_por_list': '', 'iso31662': 'IL', 'location_type': 'A', 'wiki_link': 'https://en.wikipedia.org/wiki/O%27Hare_International_Airport', 'alt_name_section': "de|Flughafen Chicago O'Hare|=wuu|奥黑尔国际机场|=th|ท่าอากาศยานนานาชาติโอแฮร์|=uk|Аеропорт О'Хара|=ta|ஓஹேர் பன்னாட்டு வானூர்தி நிலையம்|=ru|Международный аэропорт Чикаго О'Хара|=ro|Aeroportul Internațional Chicago O'Hare|=pt|Aeroporto Internacional O'Hare|=pnb|اوہیر انٹرنیشنل ہوائی اڈہ|=ja|シカゴ・オヘア国際空港|=mr|ओ'हेर आंतरराष्ट्रीय विमानतळ|=ml|ഒ'ഹെയർ അന്താരാഷ്ട്ര വിമാനത്താവളം|=hu|O’Hare nemzetközi repülőtér|=he|נמל התעופה שיקגו או'הייר|=ko|오헤어 국제공항|=fr|Aéroport international O'Hare de Chicago|=fa|فرودگاه بین\u200cالمللی اوهر شیکاگو|=es|Aeropuerto Internacional O'Hare|=de|Chicago O’Hare International Airport|=cs|Letiště Chicago O'Hare International Airport|=ar|مطار أوهير الدولي|=en|Chicago O'Hare International Airport|p=|Orchard Field|=|O'Hare International Airport|=|Orchard Place/Douglas Field|=sv|Chicago O'Hare flygplats|p", 'wac': '41', 'wac_name': 'Illinois', 'ccy_code': 'USD', 'unlc_list': 'USORD|', 'uic_list': ''}

    >>> # suppose you have a naive local datetime you want to convert
    >>> naive_loc_time = datetime(2019, 1, 1, 10, 30)

    >>> # convert your naive local date and time to utc
    >>> tz_aware_utc_time = apt.to_utc(naive_loc_time)
    >>> print(tz_aware_utc_time)
    2019-02-02 16:30:00+00:00

    >>> # convert your tz aware back to local time if you want to
    >>> tz_aware_loc_time = apt.from_utc(tz_aware_utc_time)
    >>> print(tz_aware_loc_time)
    2019-02-02 10:30:00-06:00

    >>> # ** side note ** this library internally tries to account daylight savings time (dst)
    >>> print(apt._dst(naive_loc_time, tz_aware_loc_time.tzinfo))
    False

    >>> # if you would like to update the data file, you can use:
    >>> airporttime.update()

