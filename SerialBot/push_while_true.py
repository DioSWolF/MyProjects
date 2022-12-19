import asyncio
from datetime import datetime

from random import randrange

import aiohttp
from bs4 import BeautifulSoup, element
from query_push_class import PushAnimeToday, QueryAnimeToday, SendPush
from search_dicts import SEARCH_SITE_DICT, SEARCH_TAGS_TODAY_DICT

from parse_classes import NameFindAnimeToday, EngNameAnimeToday, SeriesNumberToday, VoiceActingToday, AnimeToday, PageAnimeToday
from fake_useragent import UserAgent



async def find_new_anime_today() -> None:

    connector = aiohttp.TCPConnector(force_close=True)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        create_push_model = PushAnimeToday()

        while True:
            await asyncio.sleep(randrange(150, 250))
            # await asyncio.sleep(2)

            headers = {"User-Agent" : UserAgent().random}

            try:

                for search_key, search_site in SEARCH_SITE_DICT.items():
                    
                    async with session.get(search_site, headers=headers) as resp: 

                        soup = BeautifulSoup(await resp.text(), "lxml")

                        if resp.status == 200:

                            find_soup = SEARCH_TAGS_TODAY_DICT[search_key]["find_soup"]
                            soup = soup.select_one(find_soup)

                            await create_new_anime_today(soup, search_key, session)

                            create_push_model.create_push_record()

                            await SendPush().send_push_user()

            except aiohttp.ClientConnectionError:
                pass

                
async def create_new_anime_today(anime_today_list: BeautifulSoup, search_key: str, session) -> None:                    

    query_db = QueryAnimeToday(search_key=search_key)
    query_db.clean_records()  
    query_db.all_animeid_today()
    
    for el in anime_today_list:
        
        if isinstance(el, element.NavigableString):
            break

        anime_name = NameFindAnimeToday(el, search_key)
        series_num = SeriesNumberToday(el, search_key)
        voice_acting = VoiceActingToday(el, search_key)
        page = PageAnimeToday(el, search_key)

        headers = {"User-Agent" : UserAgent().random}
        
        if search_key == "animego":
            
            async with session.get(page.value, headers=headers) as resp: #need optimization
                
                if resp.status == 200:
                    soup = BeautifulSoup(await resp.text(), "lxml")
                    anime_eng_name = EngNameAnimeToday(soup, search_key)
                    find_anime = AnimeToday(anime_name, anime_eng_name, series_num, voice_acting, page, search_key)

                    if find_anime.anime_id not in query_db.db_list:
                        query_db.add_new_record(find_anime)

        if search_key == "anitube":
            
            anime_eng_name = EngNameAnimeToday(el, search_key)
            find_anime = AnimeToday(anime_name, anime_eng_name, series_num, voice_acting, page, search_key)

            date_anime = int(el.select_one(".story_date sup").text)
            day_now = datetime.now().day

            if find_anime.anime_id not in query_db.db_list and date_anime == day_now:
                query_db.add_new_record(find_anime)


    query_db.commit_new_records()

    return



