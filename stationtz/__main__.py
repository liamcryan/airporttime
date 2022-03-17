import csv
import shutil

import requests

from stationtz import AIRPORT_SOURCE_FILE, MANUAL_STATION_SOURCE_FILE

DATA_SOURCE_URL = 'https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv'


def create_stations(file, **kwargs):
    """ Manually specify stations"""
    with open(file, "rt") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assert (row.get("icao_code") or row.get("iata_code")) and row.get("timezone")

    print(f"Copying file to {MANUAL_STATION_SOURCE_FILE}")
    shutil.copyfile(file, MANUAL_STATION_SOURCE_FILE)


def update_airports(*args, **requests_kwargs):
    """ Update the ori_por_public.csv file directly from source.

    :param requests_kwargs: any kwargs you would like to pass to the requests.get method
            proxy={'http': '', 'https': ''}  <- might be useful if you are requesting within proxy server

    """
    r = requests.get(DATA_SOURCE_URL, **requests_kwargs)

    print(f"Updating {AIRPORT_SOURCE_FILE}")
    with open(AIRPORT_SOURCE_FILE, 'wt', encoding='utf-8') as f:
        f.write(r.text)


if __name__ == '__main__':
    import argparse

    scripts = ["update_airports", "create_stations"]

    parser = argparse.ArgumentParser(
        description="Utility to set data used by this library.")
    parser.add_argument("script", help=f"Choose the script to run: {scripts}", type=str)
    parser.add_argument("--arg", help=f"Any argument required by the script", type=str)
    parser.add_argument("--kwarg", help=f"Any keyword argument used by the script", type=str)
    args = parser.parse_args()

    if args.script in scripts:
        arg = args.arg if args.arg else []

        kwarg = {args.kwarg.split("=")[0]: args.kwarg.split("=")[1]} if args.kwarg else {}
        eval(args.script)(arg, **kwarg)
    else:
        raise Exception(f"Valid values for script are: {scripts}")
