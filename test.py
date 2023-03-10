import requests

base_url = 'https://reiseauskunft.bahn.de/bin/query.exe/dn'

params = {
    'protocol': 'https:',
    'REQ0JourneyStopsS0G' : 'Enzberg'
}

response = requests.get(f'{base_url}/', params=params)
data = response.json()

print(data)