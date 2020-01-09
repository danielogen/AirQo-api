import requests

url = 'http://localhost:5000/geo_coordinates'
r = requests.post(url,json=device_json)

print(r.json())