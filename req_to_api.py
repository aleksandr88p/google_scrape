import requests
import json


keyword = 'lada kalina'
country = 'us'
url = f"http://185.51.121.22:8000/process_string/{keyword}/{country}"
response = requests.get(url)

print(response.json())
print(json.dumps(response.json(), indent=4))