
from io import StringIO
import requests


import csv


def station_api(bahnhof_name):
    url = f'https://v6.db.transport.rest/stations?query={bahnhof_name}&limit=1'     #https://v6.db.transport.rest/api.html#get-stationss
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        try:
            closest_id = list(data.keys())[0]
            eva = data[closest_id]['id']
        except:
           eva = station_csv(bahnhof_name)
    else:
        eva = station_csv(bahnhof_name)
    return eva

def station_csv(bahnhof_name):
    # search for the station in the csv file
    data = open("Verzeichnis/bahnhofsverzeichnis.csv", "r").read()
    f = StringIO(data)
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        if row['NAME'] == bahnhof_name:
            return row['EVA_NR']
    return "Station not found"

