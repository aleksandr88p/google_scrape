from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import datetime
import random
from requests.exceptions import ProxyError, HTTPError
from httpx import AsyncClient
import json
from httpx import AsyncHTTPTransport, URL, AsyncClient, Proxy
import httpx
import asyncio

"""
pip install fastapi uvicorn

uvicorn OLD_api:app --reload  local

uvicorn asyncApi:app --host 185.51.121.22 --port 8000  on server

"""


successful_requests = 0


class MyAPI:
    def __init__(self):
        pass

    async def make_request(self, keyword: str, country: str) -> str:
        print(keyword, country)
        proxy_url = URL('http://83.149.70.159:13012')
        # transport = AsyncHTTPTransport(proxy=httpx.Proxy(url=proxy_url))
        transport = AsyncHTTPTransport(proxy=httpx.Proxy(url=str(proxy_url)))
        async with AsyncClient(transport=transport) as client:
            # async with AsyncClient() as client:

            cookies = {}
            headers = {
                'authority': 'www.google.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'ru',
                'cache-control': 'max-age=0',
                'dnt': '1',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-bitness': '"64"',
                'sec-ch-ua-full-version': '"110.0.5481.100"',
                'sec-ch-ua-full-version-list': '"Chromium";v="110.0.5481.100", "Not A(Brand";v="24.0.0.0", "Google Chrome";v="110.0.5481.100"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Linux"',
                'sec-ch-ua-platform-version': '"5.19.0"',
                'sec-ch-ua-wow64': '?0',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.{random.randint(0, 9999)} Safari/537.{random.randint(0, 99)}',
            }

            params = {
                'q': f'{keyword}',
                # 'uule': 'w CAIQICINVW5pdGVkIFN0YXRlcw',
                'gl': f'{country}',  # geographic location gl=us USA gl=uk Great Britain
                'hl': 'en',  # language interface hl=en hl=ru
                # 'lr': 'lang_en' # Search language
            }

            while True:
                try:
                    await asyncio.sleep(1)
                    response = await client.get('https://www.google.com/search', params=params, cookies=cookies,
                                                headers=headers, timeout=(10, 10))

                    response.raise_for_status()  # Проверка на HTTP ошибки

                    return response.text
                    await asyncio.sleep(0.1)

                except Exception as ex:
                    print(ex)
                    return await self.make_request(keyword=keyword, country=country)

    def searching_parameters(self, soup):
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

    def searching_information(self, soup):
        try:
            google_page = 'https://google.com'
            search_info_box_raw = soup.find('div', attrs={"role": "navigation"}).find_all('a')
            # search_info_box = search_info_box_raw.find_all('a')
            search_navigator_box = []
            for num, oneA in enumerate(search_info_box_raw):
                to_list = [num + 1, oneA.text, oneA['href']]
                if 'https://' not in to_list[2]:
                    to_list[2] = google_page + to_list[2]
                search_navigator_box.append(to_list)
            results = soup.find('div', attrs={'id': 'result-stats'}).find('nobr').previous_sibling
            time_taken = soup.find('div', attrs={'id': 'result-stats'}).find('nobr').text.strip()
            # print(search_navigator_box)
            # print(results.text)
            # print(time_taken)
            return {"searching_info": {'navigator_box': search_navigator_box, 'total_results': results.text,
                                       'time_taken_displayed': time_taken}}
        except Exception as e:
            print(f'error in searching information {e}')

    def scrolling_carousel(self, soup):

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
                    # all_tweets.append([tweet_date, now_utc, snippet.text, link, status_link])
                except Exception as e:
                    # print(f'error in one tweet {card} {e}')
                    pass
            tweet_dict = {}
            try:
                for num, elem in enumerate(all_tweets):
                    tweet_dict[num + 1] = elem
            except Exception as e:
                print(f'error in tweet dict in scrolling_carousel {e}')

            return {'inline_tweets': tweet_dict}

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

    def searching_organic(self, soup):
        # all_organic = soup.select('div.g')
        organic_list = []
        organic_dict = {}
        all_organic = soup.find_all('div', class_='g')

        for num, item in enumerate(all_organic):
            try:
                link = item.find('a')['href']
                head = item.find('h3').text
                # print(head)
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
        soup = BeautifulSoup(content, 'html.parser')
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
