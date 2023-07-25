import asyncio

from bs4 import BeautifulSoup
import datetime
from urllib.parse import urlparse
import json


class MobileScrape:

    def __init__(self):
        self.gen_link = 'https://www.google.com'

    #####################
    # search parameters #
    #####################
    def searching_parameters(self, soup):
        '''
        searching  parametrs(keyword, language, device
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


    ##############
    # also search#
    ##############
    def also_search(self, soup):

        # all_items = soup.find('div', attrs={'class': 'ouy7Mc'}).find_all('div', attrs={'jsname': 'Cpkphb'})
        all_items = soup.find_all('div', attrs={'class': 'ouy7Mc'})
        for item in all_items:
            if item.find_all('div', attrs={'jsname': 'Cpkphb'}):
                all_search = item.find_all('div', attrs={'jsname': 'Cpkphb'})
            # if item.find_all('div', attrs={'jsname': 'yEVEwb'}):
            #     all_quest = item.find_all('div', attrs={'jsname': 'yEVEwb'})
        also_search_list = []
        try:
            for item in all_search:
                query = item.text.strip()
                link_raw = item.find('a')['href']
                link = f"{self.gen_link}{link_raw}"
                also_search_list.append({'query': query, 'link': link})
        except Exception as e:
            print(f'error in also search in mobile vers\n{e}')
        return also_search_list


    ############
    # also ask #
    ############

    # def also_ask(self, soup):



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

            return tweet_dict

    ###############
    # top stories #
    ###############
    def searching_top_stories(self, soup):
        all_stories = soup.find_all('a', attrs={'class': 'WlydOe'})
        # top_stories = {}
        top_stories = []
        for num, story in enumerate(all_stories):
            try:
                story_date = story.find_all('span')[-1].text
                snippet = story.text.replace(story_date, '')
                # top_stories[num + 1] = {'date': story_date, 'snippet': snippet, 'link': story['href']}
                top_stories.append({'date': story_date, 'snippet': snippet, 'link': story['href']})
            except Exception as e:
                print(f'error in top stories {e}')

        return top_stories

    ###################
    # organic results #
    ###################
    def searching_organic(self, soup):
        organic_list = []
        # Ww4FFb vt6azd g
        all_organic = soup.find_all('div', class_='kvH3mc BToiNc UK95Uc')
        c = 0
        for num, item in enumerate(all_organic):
            try:
                link = item.find('a')['href']
                head = item.find('div', attrs={'class': 'oewGkc LeUQr MUxGbd v0nnCb'}).text
                head = ' '.join(head.strip().split())
                # VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf
                try:
                    snippet = item.find('div', class_='VwiC3b').text
                except:
                    snippet = ' '
                if snippet:
                    c += 1
                try:
                    d_key = urlparse(link).netloc
                except:
                    d_key = ''
                    print('error in domain in organic')
                organic_list.append(
                    {'position': f'{c}', 'domain_key': d_key, 'title': head, 'snippet': snippet, 'link': link})
            except Exception as e:
                print(f'error in organic results in {e}')
        return organic_list

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
                # print(title)
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
                return knowl_dict

            except Exception as e:
                print(f'error in knowledge item {e}')
                # knowl_dict = {}

    def searching_sponsored(self, soup):
        """
        :param soup:
        :return:
        """
        all_sponsored = soup.find_all('div', attrs={'class': 'uEierd'})
        spons = []

        for item in all_sponsored:
            # print(item)

            try:
                sponsor_name = item.find('span', class_='BTu2cd VpN09').text
                sponsor_link = item.find('a', class_='sVXRqc')
                title = sponsor_link.find('span').text
                spons_descr = item.find('div', class_='MUxGbd yDYNvb lyLwlc').text
                spons_descr = " ".join(spons_descr.split())
                sublincs = item.find('div', class_='dcuivd MUxGbd lyLwlc aLF0Z OSrXXb')
                if sublincs:
                    # print('sublincs')
                    sublincs_list = []
                    all_links = sublincs.find_all('a')
                    for link in all_links:
                        sub_title = link.text
                        sub_title = " ".join(sub_title.split())
                        sub_link = link['href']
                        # print(sub_title)
                        # print(sub_link)
                        sublincs_list.append({sub_title: sub_link})
                    spons.append({'sponsor_name': sponsor_name, 'sponsor_link': sponsor_link['href'], 'title': title,
                                  'spons_descr': spons_descr, 'sublincs': sublincs_list})
                else:
                    spons.append({'sponsor_name': sponsor_name, 'sponsor_link': sponsor_link['href'], 'title': title,
                                  'spons_descr': spons_descr})
            except Exception as e:
                print(f'error in ads(sponsored) {e}')

        return spons

    def map_and_places(self, soup):
        map_dict = {}
        places = []
        try:
            upThe_map = soup.find('div', attrs={"class": "H93uF"})
            link_to_map = f"https://www.google.com/{upThe_map.find('a')['href']}"
            map_dict['link_to_map'] = link_to_map
        except:
            link_to_map = None
        items_below_the_map = soup.find_all('div', attrs={"class": "VkpGBb"})
        for item in items_below_the_map:
            try:
                left_side = item.find('div', attrs={'class': 'rllt__details'})
                heading = left_side.find(attrs={'role': 'heading'}).text
                text = left_side.text
                clear_text = [item.text for item in left_side]
                places.append({'heading': heading, 'text': clear_text})
            except Exception as ex:
                print(f'error occured in below the map section {ex}')
                return None
        map_dict['places'] = places
        return map_dict

    def searching_images(self, soup):
        image_list = []
        try:
            all_items = soup.find_all('div', attrs={'jsname': 'dTDiAc'})
            for num, item in enumerate(all_items):
                image = item.find('img')['src']
                link = item['data-lpage']
                title = item.find('img')['alt']
                image_list.append({'image': image, 'link': link, 'title': title})
        except Exception as e:
            print(f'error in image {e}')
        return image_list

    def searching_video(self, soup):
        if soup.find_all(attrs={'class': 'BycXVc'}):
            all_vids = soup.find_all(class_='BycXVc')
            video_list = []
            for num, video in enumerate(all_vids):
                try:
                    position = num + 1
                    a_tag = video.find_all('a')
                    title = a_tag[-1].find(class_='WDJH5').text
                    link = a_tag[-1]['href']
                    source = a_tag[-1].find(class_='PUDiTd o5sVue OSrXXb').text
                    date = a_tag[-1].find(class_='o5sVue OSrXXb').text
                    video_list.append({'title': title, 'link': link, 'source': source, 'date': date})
                except Exception as e:
                    print(f'error occured in videos {e}')
            return video_list

    async def make_json(self, content):
        soup = BeautifulSoup(content, 'lxml')
        to_json = {}
        to_json['params'] = self.searching_parameters(soup)
        # to_json['info'] = self.searching_information(soup)
        to_json['organic'] = self.searching_organic(soup)
        to_json['top_stories'] = self.searching_top_stories(soup)
        to_json['inline_tweets'] = self.scrolling_carousel(soup)
        to_json['knowledge'] = self.searching_knowledge(soup)
        to_json['maps'] = self.map_and_places(soup)
        to_json['videos'] = self.searching_video(soup)
        to_json['images'] = self.searching_images(soup)
        to_json['ads'] = self.searching_sponsored(soup)
        to_json['also_search'] = self.also_search(soup)
        # my_json = json.dumps(to_json, indent=4, ensure_ascii=False)
        return to_json



scrap = MobileScrape()

# with open('../OLD/google_searchOLD/for_api_test/last_of_us_mob.html', 'r') as f:
#     cont = f.read()
#
# d = asyncio.run(scrap.make_json(cont))
# # print(scrap.gen_link)
# print(json.dumps(d,indent=4))