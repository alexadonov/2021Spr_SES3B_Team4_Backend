import requests
import os, json

base_url = 'http://127.0.0.1:8000/api'
script_dir = os.path.dirname(__file__)

def populate(endpoint, file_name):
    data_file = os.path.join(script_dir, file_name)
    
    with open(data_file, 'r') as data:
        items = json.load(data)
        total_items = len(items)
        for i, item in enumerate(items):
            r = requests.post(base_url + endpoint, json=item)
            if r.status_code != 201:
                print('An error occured: ' + r.json()['message'])
                break
            print('{0:.0%} of {1} rows added'.format(i/total_items, total_items), end='\r')
    print()

def populate_events():
    populate('/create-event', 'event_data.json')

populate_events()