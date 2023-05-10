import json
from parse_dekstop import DekstopScrape
from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import datetime
import random
from requests.exceptions import ProxyError, HTTPError
from fastapi.middleware.cors import CORSMiddleware
# Подрубаешь модуль мой
from mod_req import AsyncReq

"""
pip install fastapi uvicorn

uvicorn OLD_api:app --reload  local
uvicorn google_api1:app --reload  
uvicorn api_google2:app --host 185.51.121.22 --port 8000  on server

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
        self.headers = {
            'authority': 'www.google.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',

            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            # 'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.{random.randint(0, 9999)} Safari/537.{random.randint(0, 99)}',
        }

        self.base_url = 'https://www.google.com'

    async def make_request(self, keyword: str, country: str) -> str:
        try:

            proxies = 'http://83.149.70.159:13012'
            # proxies = 'http://astroproxy4014:50bd57@51.89.94.97:11079'
            params = {
                'q': keyword,
                # 'uule': 'w CAIQICINVW5pdGVkIFN0YXRlcw',
                'gl': 'us',  # geographic location gl=us USA gl=uk Great Britain
                'hl': 'en',  # language interface hl=en hl=ru
                # 'lr': 'lang_en' # Search language
            }
            # resp = await self.return_responses(url=f"{self.base_url}/search", params=params,
            #                                    headers=self.headers, proxies=proxies)
            resp = await self.return_responses(url=f"{self.base_url}/search", params=params,
                                               headers=self.headers)

            print(resp.real_url)
            if resp is None:
                # raise BadProxies
                print('None .... BadProxies')
                return await self.make_request(keyword=keyword, country=country)

            if 'consent.google.com' in resp.real_url:
                # raise BadResponse
                print('consent.google.com')
                return await self.make_request(keyword=keyword, country=country)
            elif resp.status in [200]:
                # Делаешь что нужно
                print(200)
                return resp.text

            elif resp.status in [401]:
                print('[401] .... BadProxies')
                return await self.make_request(keyword=keyword, country=country)

            elif resp.status in [409]:
                print('[409] .... BadProxies')
                return await self.make_request(keyword=keyword, country=country)
            else:
                print(f'else .... BadProxies {resp.status} |')
                return await self.make_request(keyword=keyword, country=country)
        except Exception as e:
            return await self.make_request(keyword=keyword, country=country)




my_api = MyAPI()
dekstop_scrapper = DekstopScrape()

@app.get("/")
async def root():
    return {"message": "Hello to google scraper"}


@app.get("/process_string/{keyword}/{country}/{req_type}")
async def process_string(keyword: str, country: str, req_type: str):
    global successful_requests
    while True:
        content = await my_api.make_request(keyword, country)
        result_json = await dekstop_scrapper.make_json(content)
        if result_json.get('params'):
            successful_requests += 1
            # my_json = json.dumps(result_json, indent=4, ensure_ascii=False)
            # return my_json
            return result_json
            # return json.loads(result_json, ensure_ascii=False)

@app.get("/stats")
async def stats():
    global successful_requests

    return {"successful_requests": successful_requests}