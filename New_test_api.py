import requests
import json
import urllib.parse

base_url = 'http://185.51.121.22:8000'

keyword = 'alfa romeo Giulia'
encoded_keyword = urllib.parse.quote(keyword)
location = 'usa'
country = 'usa'
device = 'mobile'
token = '116873402439359'
email = 'gebamo5450@camplvad.com'

url = f"{base_url}/process_string/{encoded_keyword}/{location}/{country}/{device}?token={token}&email={email}"
print(url)
resp = requests.get(url)

if resp.status_code == 200:
    json_response = resp.json()
    # Вывод с отступами (indent=4)
    print(json.dumps(json_response, indent=4, ensure_ascii=False))
else:
    print(f"error {resp.status_code} - {resp.text}")