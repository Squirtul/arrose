
# gets data from vatty

import requests

url = "https://data.vatsim.net/v3/vatsim-data.json"

def get_vatsim_data():
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()
