import json
from parse_dekstop import DekstopScrape
from parse_mobile import MobileScrape
from fastapi import FastAPI
from fastapi import Query
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import datetime
import random
from requests.exceptions import ProxyError, HTTPError
from fastapi.middleware.cors import CORSMiddleware
from interaction_with_db import get_all_users, change_available_request_value, get_specific_user
from mod_req import AsyncReq
import base64

"""
pip install fastapi uvicorn

uvicorn OLD_api:app --reload  local
uvicorn google_api1:app --reload  
uvicorn google_api1:app --host 185.51.121.22 --port 8000  on server
uvicorn google_api1:app --host 185.51.121.22 --port 8000

"""
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

successful_requests = 0


class MyAPI(AsyncReq):
    def __init__(self):
        super().__init__()
        self.dekstop_headers = {
            'authority': 'www.google.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            # 'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.{random.randint(0, 9999)} Safari/537.{random.randint(0, 99)}',
        }

        self.mobile_heders = {
            'authority': 'www.google.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1'
        }

        self.base_url = 'https://www.google.com'

    async def make_request(self, keyword: str, location: str, country: str, device: str) -> str:

        device = device.lower()
        city_name_base64 = base64.b64encode(location.encode('utf-8')).decode('utf-8')
        uule = "w+CAIQICI" + chr(len(location)) + city_name_base64

        try:
            # proxies = 'http://83.149.70.159:13012' # On SERVER
            proxies = None # on local
            # proxies = 'http://astroproxy4014:50bd57@51.89.94.97:11079'
            params = {
                'q': keyword,
                # 'uule': 'w CAIQICINVW5pdGVkIFN0YXRlcw',
                'uule': uule,
                'gl': country,  # geographic location gl=us USA gl=uk Great Britain
                'hl': 'en',  # language interface hl=en hl=ru
                # 'lr': 'lang_en' # Search language
            }
            # resp = await self.return_responses(url=f"{self.base_url}/search", params=params,
            #                                    headers=self.headers, proxies=proxies)

            if device not in ["mobile", "desktop"]:
                return {"device error": "input mobile or desktop"}
            if device.startswith('m') or device.startswith('M'):
                resp = await self.return_responses(url=f"{self.base_url}/search", params=params,
                                                   headers=self.mobile_heders, proxies=proxies)
            else:
                resp = await self.return_responses(url=f"{self.base_url}/search", params=params,
                                                   headers=self.dekstop_headers, proxies=proxies)
            print(resp.real_url)
            if resp is None:
                # raise BadProxies
                print('None .... BadProxies')
                return await self.make_request(keyword=keyword, location=location, country=country, device=device)

            if 'consent.google.com' in resp.real_url:
                # raise BadResponse
                print('consent.google.com')
                return await self.make_request(keyword=keyword, location=location, country=country, device=device)
            elif resp.status in [200]:
                # Делаешь что нужно
                print(200)
                return resp.text

            elif resp.status in [401]:
                print('[401] .... BadProxies')
                return await self.make_request(keyword=keyword, location=location, country=country, device=device)

            elif resp.status in [409]:
                print('[409] .... BadProxies')
                return await self.make_request(keyword=keyword, location=location, country=country, device=device)
            else:
                print(f'else .... BadProxies {resp.status} |')
                return await self.make_request(keyword=keyword, location=location, country=country, device=device)
        except Exception as e:
            return await self.make_request(keyword=keyword, location=location, country=country, device=device)




my_api = MyAPI()
dekstop_scrapper = DekstopScrape()
mobile_scrapper = MobileScrape()


@app.get("/")
async def root():
    return {"message": "Hello to google scraper"}


@app.get("/process_string/{keyword}/{location}/{country}/{device}")
async def process_string(
        keyword: str,
        location: str,
        country: str,
        device: str,
        token: str = Query(...),
        email: str = Query(...)
        ):
    global successful_requests
    specific_user = get_specific_user(email)
    if len(specific_user) > 0:
        # print(specific_user[0]['user_email'])

        available_reqs = int(specific_user[0]['available_requests'])
        if not token == specific_user[0]['unique_token']:
            return {"Token": "token error"}
        if available_reqs < 1:
            return {"available_requests": "not enough available_requests"}

        print(f"token {specific_user[0]['unique_token']}, reqs {available_reqs}")
        while True:
            content = await my_api.make_request(keyword, location, country, device)
            # print(content)
            # with open('first.html', 'a') as f:
            #     f.write(content)
            if device.startswith('m') or device.startswith('M'):
                result_json = await mobile_scrapper.make_json(content)
            else:
                result_json = await dekstop_scrapper.make_json(content)
            if result_json.get('params'):
                successful_requests += 1
                # my_json = json.dumps(result_json, indent=4, ensure_ascii=False)
                # return my_json
                change_available_request_value(email=email, new_value=str(available_reqs - 1))
                return result_json
                # return json.loads(result_json, ensure_ascii=False)
    else:
        return {"email": "Not correct email or There is no user with such credentials in the database."}

@app.get("/stats")
async def stats():
    global successful_requests

    return {"successful_requests": successful_requests}