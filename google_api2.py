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
            resp = await self.return_responses(url=f"{self.base_url}/search", params=params,
                                               headers=self.headers, proxies=proxies)
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

    #####################
    # search parameters #
    #####################
    def searching_parameters(self, soup):
        '''
        searching  parametrs(keyword, language, location
        :param soup:
        :return:
        '''
        try:
            # search_box = soup.select_one('input[name="q"]')
            search_box = soup.find(attrs={'name': 'q'})
            search_query = search_box['value']
            location_box = soup.select_one('input[name="gl"]')
            location = location_box['value']
            language_box = soup.select_one('input[name="hl"]')
            language = language_box['value']
            return {'searching_parameters': {'search_query': search_query, 'location': location, 'language': language}}
        except Exception as e:
            print(f'error in searching parameters {e}')

    #############################################################
    # search information (search_tabs(news, images, videos, etc #
    #############################################################
    def searching_information(self, soup):
        '''
        searching info in google result(num of res and time
        :param soup:
        :return:
        '''
        try:
            google_page = 'https://google.com'
            search_info_box_raw = soup.find('div', attrs={"role": "navigation"}).find_all('a')
            search_navigator_box = []
            for num, oneA in enumerate(search_info_box_raw):
                to_list = [num + 1, oneA.text, oneA['href']]
                if 'https://' not in to_list[2]:
                    to_list[2] = google_page + to_list[2]
                search_navigator_box.append(to_list)
            results = soup.find('div', attrs={'id': 'result-stats'}).find('nobr').previous_sibling
            time_taken = soup.find('div', attrs={'id': 'result-stats'}).find('nobr').text.strip()
            return {"searching_info": {'navigator_box': search_navigator_box, 'total_results': results.text,
                                       'time_taken_displayed': time_taken}}
        except Exception as e:
            print(f'error in searching information {e}')

    #################
    # inline tweets #
    #################
    def scrolling_carousel(self, soup):
        '''
        if twitter cards in google serp
        :return:
        '''
        all_cards = soup.find_all('g-inner-card')
        if all_cards:
            all_tweets = []
            for card in all_cards:
                try:
                    link = card.find('a')['href']
                    time_and_social = [i.text for i in card.find_all('span') if i.text != '']
                    if 'ago' in time_and_social[-1]:
                        tweet_date = time_and_social[-1]
                    else:
                        tweet_date = ''

                    status_link = link
                    link = link.split('status/')[0]

                    now_utc = str(datetime.datetime.utcnow())
                    snippet = card.find('div', attrs={"class": "tw-res"})
                    all_tweets.append(
                        {'tweet_date': tweet_date, 'now_utc': now_utc, 'snippet': snippet.text, 'link': link,
                         'status_link': status_link})
                except Exception as e:
                    pass
            tweet_dict = {}
            try:
                for num, elem in enumerate(all_tweets):
                    tweet_dict[num + 1] = elem
            except Exception as e:
                print(f'error in tweet dict in scrolling_carousel {e}')

            return {'inline_tweets': tweet_dict}

    ###############
    # top stories #
    ###############
    def searching_top_stories(self, soup):
        all_stories = soup.find_all('a', attrs={'class': 'WlydOe'})
        top_stories = {}
        for num, story in enumerate(all_stories):
            try:
                story_date = story.find_all('span')[-1].text
                snippet = story.text.replace(story_date, '')
                top_stories[num + 1] = {'date': story_date, 'snippet': snippet, 'link': story['href']}
            except Exception as e:
                print(f'error in top stories {e}')

        return {'top_stories': top_stories}

    ###################
    # organic results #
    ###################
    def searching_organic(self, soup):
        organic_list = []
        organic_dict = {}
        all_organic = soup.find_all('div', class_='g')

        for num, item in enumerate(all_organic):
            try:
                link = item.find('a')['href']
                head = item.find('h3').text
                # VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf
                try:
                    snippet = item.find('div', class_='VwiC3b').text
                except:
                    snippet = ''
                if snippet:
                    organic_dict[num + 1] = {'title': head, 'snippet': snippet, 'link': link}
            except Exception as e:
                pass
        return {'organic_results': organic_dict}

    def searching_knowledge(self, soup):
        """
        looking for a knowlege in serp Google
        :param soup:
        :return:
        """
        knowl_dict = {}
        if soup.find(class_='kp-wholepage'):

            try:
                knowlege = soup.find('div', class_='kp-wholepage')
                title = knowlege.find(attrs={"data-attrid": 'title'}).text
                print(title)
                subtitle = knowlege.find(attrs={"data-attrid": 'subtitle'}).text
                description = knowlege.select_one(".kno-rdesc span").text
                raw_link = knowlege.select_one(".kno-rdesc a")
                table_data = knowlege.find_all(attrs={"class": 'rVusze'})
                try:
                    link = raw_link['href']
                    source = raw_link.text
                except:
                    link = None
                    source = None
                knowl_dict = {'title': title, 'subtitle': subtitle,
                              'description': description, 'link': link, 'source': source}

                for item in table_data:
                    name = item.find(attrs={'class': 'w8qArf'}).text
                    # print(f'name = {name}')

                    values_in_item = item.find_all(attrs={'class': 'LrzXr kno-fv wHYlTd z8gr9e'})
                    for i in values_in_item:
                        # print(i.text)
                        # print(f'i = {i.text}')
                        # knowl_dict[name] = [i.text]
                        if i.find('a'):
                            all_link_in_item = i.find_all('a')
                            items_dict = {}
                            for item in all_link_in_item:
                                items_dict[item.text] = f"https://www.google.com/{item['href']}"
                                # items_dict['displayed_link'] = item.text
                                # items_dict['link'] = f"https://www.google.com/{item['href']}"
                            knowl_dict[name] = items_dict
                        else:
                            knowl_dict[name] = [i.text]
                    # print('************************')
                return {'knowledge': knowl_dict}

            except Exception as e:
                print(f'error in knowledge item {e}')
                knowl_dict = {}

    def searching_sponsored(self, soup):
        """

        :param soup:
        :return:
        """
        all_sponsored = soup.find_all(attrs={"class": "uEierd"})
        for sponsor in all_sponsored:
            print(sponsor.text)

    def map_and_places(self, soup):
        map_dict = {}
        try:
            upThe_map = soup.find('div', attrs={"class": "H93uF"})
            link_to_map = f"https://www.google.com/{upThe_map.find('a')['href']}"
            map_dict['link_to_map'] = link_to_map
            map_dict['places'] = {}
        except:
            link_to_map = None

        items_below_the_map = soup.find_all('div', attrs={"class": "VkpGBb"})
        for item in items_below_the_map:
            try:
                left_side = item.find('div', attrs={'class': 'rllt__details'})
                heading = left_side.find(attrs={'role': 'heading'}).text
                text = left_side.text
                # links = item.find_all('a')
                # print(links[-2]['href'])
                # print(len(links))
                clear_text = [item.text for item in left_side]
                map_dict['places'][heading] = clear_text
            except Exception as ex:
                print(f'error occured in below the map section {ex}')
                return None

        return map_dict

    def searching_video(self, soup):
        if soup.find_all(attrs={'class': 'RzdJxc'}):
            all_vids = soup.find_all(class_='RzdJxc')
            # video_dict = {'inline_videos': []}

            video_dict = {'inline_videos': {}}
            for num, video in enumerate(all_vids):
                try:
                    position = num + 1
                    a_tag = video.find_all(class_='X5OiLe')
                    title = a_tag[-1].find(class_='cHaqb').text
                    link = a_tag[-1]['href']
                    source = a_tag[-1].find(class_='pcJO7e').text
                    date = a_tag[-1].find(class_='hMJ0yc').text
                    # print(position, title, link, source, date)
                    video_dict['inline_videos'][position] = {'title': title, 'link': link, 'source': source,
                                                             'date': date}

                except Exception as e:
                    print(f'error occured in videos {e}')
            return video_dict

    async def make_json(self, content):
        soup = BeautifulSoup(content, 'lxml')
        to_json = {}
        to_json['params'] = self.searching_parameters(soup)
        to_json['info'] = self.searching_information(soup)
        to_json['organic'] = self.searching_organic(soup)
        to_json['top_stories'] = self.searching_top_stories(soup)
        to_json['inline_tweets'] = self.scrolling_carousel(soup)
        to_json['knowledge'] = self.searching_knowledge(soup)
        to_json['maps'] = self.map_and_places(soup)
        to_json['videos'] = self.searching_video(soup)

        return to_json


my_api = MyAPI()


@app.get("/")
async def root():
    return {"message": "Hello to google scraper"}


@app.get("/process_string/{keyword}/{country}")
async def process_string(keyword: str, country: str):
    global successful_requests
    while True:
        content = await my_api.make_request(keyword, country)
        result_json = await my_api.make_json(content)
        if result_json.get('params'):
            successful_requests += 1
            return result_json


@app.get("/stats")
async def stats():
    global successful_requests

    return {"successful_requests": successful_requests}