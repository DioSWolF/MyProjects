#!/usr/bin/env python
# -*- coding: utf-8 -*-


import asyncio
from datetime import datetime, timedelta

from random import randrange

import aiohttp
from bs4 import BeautifulSoup, element
from classes.push_query import PushAnimeToday, QueryAnimeToday, SendPush
from config.search_dicts import SEARCH_SITE_DICT, SEARCH_TAGS_TODAY_DICT

from parse.push_user import NameFindAnimeToday, EngNameAnimeToday, SeriesNumberToday, VoiceActingToday, AnimeToday, PageAnimeToday, DateUpdate
from fake_useragent import UserAgent



async def find_new_anime_today() -> None:

    connector = aiohttp.TCPConnector(force_close=True)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        create_push_model = PushAnimeToday()

        while True:
            await asyncio.sleep(randrange(150, 250))

            headers = {"User-Agent" : UserAgent().random}

            try:

                for search_key, search_site in SEARCH_SITE_DICT.items():
                    parse_site = f"{search_site['link']}{search_site['page_list']}"

                    for num_page in range(1, 6):
                        
                        async with session.get(parse_site, headers=headers) as resp: 

                            parse_site = f"{search_site['link']}{search_site['page_list']}{num_page}"
                            soup = BeautifulSoup(await resp.text(), "lxml")
                            
                            if resp.status == 200:

                                find_soup = SEARCH_TAGS_TODAY_DICT[search_key]["find_soup"]
                                soup_t = soup.select_one(find_soup)

                                stop = await create_new_anime_today(soup_t, search_key, session)
                                

                                if stop == "stop":
                                    break

                create_push_model.create_push_record()
                                
                await SendPush().send_push_user()

            except aiohttp.ClientConnectionError:
                pass

                
async def create_new_anime_today(anime_today_list: BeautifulSoup, search_key: str, session: aiohttp.ClientSession) -> None:                    

    query_db = QueryAnimeToday(search_key=search_key)
    query_db.clean_records()  
    query_db.all_animeid_today()

    stop = ""

    for el in anime_today_list:
        day_now = (datetime.now() + timedelta(hours=2)).day

        try:
            if isinstance(el, element.NavigableString):# or DateUpdate(el, search_key).value != day_now:
                query_db.commit_new_records()
                break 

            if DateUpdate(el, search_key).value != day_now:
                query_db.commit_new_records()
                return "stop"

        except AttributeError:
            query_db.commit_new_records()
            break 
            
        func_add = SITE_FUNC_DICT[search_key]
        stop = await func_add(el, search_key, query_db, session)
    query_db.commit_new_records()
    return stop


async def add_anitube(el: BeautifulSoup, search_key: str,  query_db: QueryAnimeToday, session: aiohttp.ClientSession) -> None:

    anime_name = NameFindAnimeToday(el, search_key)
    series_num = SeriesNumberToday(el, search_key)
    voice_acting = VoiceActingToday(el, search_key)
    page = PageAnimeToday(el, search_key)
    anime_eng_name = EngNameAnimeToday(el, search_key)

    find_anime = AnimeToday(anime_name, anime_eng_name, series_num, voice_acting, page, search_key)

    if find_anime.anime_id not in query_db.db_list:

        for series in series_num.value:
            ser_num = SeriesNumberToday(series, search_key)

            voice_list = voice_acting.value.get(ser_num.value)
                       
            for voice in voice_list:
                if voice != "":
                    voice_act = VoiceActingToday(voice, search_key)
                    find_anime = AnimeToday(anime_name, anime_eng_name, ser_num, voice_act, page, search_key)
                    query_db.add_new_record(find_anime)


async def add_animego(el: BeautifulSoup, search_key: str,  query_db: QueryAnimeToday, session: aiohttp.ClientSession) -> None:

    anime_name = NameFindAnimeToday(el, search_key)
    series_num = SeriesNumberToday(el, search_key)
    voice_acting = VoiceActingToday(el, search_key)
    page = PageAnimeToday(el, search_key)

    headers = {"User-Agent" : UserAgent().random}

    async with session.get(page.value, headers=headers) as resp: #need optimization

        if resp.status == 200:
            soup = BeautifulSoup(await resp.text(), "lxml")
            anime_eng_name = EngNameAnimeToday(soup, search_key)

            find_anime = AnimeToday(anime_name, anime_eng_name, series_num, voice_acting, page, search_key)

            query_db.add_new_record(find_anime)
    return "stop"

SITE_FUNC_DICT = {"animego" : add_animego, "anitube" : add_anitube}




