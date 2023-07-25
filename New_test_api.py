import requests

base_url = 'http://185.51.121.22:8000'

keyword = 'alfa romeo'
location = 'usa'
country = 'usa'
device = 'mobile'
token = '116873402439359'
email = 'gebamo5450@camplvad.com'

url = f"{base_url}/process_string/{keyword}/{location}/{country}/{device}?token={token}&email={email}"

resp = requests.get(url)

if resp.status_code == 200:
    print(resp.json())
else:
    print(f"error {resp.status_code} - {resp.text}")