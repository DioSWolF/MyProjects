#!/usr/bin/env python
# -*- coding: utf-8 -*-


import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

from datetime import datetime, timedelta
from bs4 import BeautifulSoup, element
from fake_useragent import UserAgent
from random import randrange

from config.bot_token import server_time
from config.search_dicts import SEARCH_SITE_DICT, SEARCH_TAGS_TODAY_DICT

from classes.push_query import PushAnimeToday, QueryAnimeToday, SendPush
from classes.ongoing_list import OngoingAnime
from classes.analitic import AnaliticUserData

from parse.push_user import NameFindAnimeToday, EngNameAnimeToday, SeriesNumberToday, VoiceActingToday, AnimeToday, PageAnimeToday, DateUpdate


# scheduler = AsyncIOScheduler({'apscheduler.job_defaults.max_instances': 2})


async def find_ongoing():
    ogoing_find = OngoingAnime()
    await ogoing_find.find_anime_ongoing()


async def analitic_user_data():
    analitic = AnaliticUserData()
    analitic.create_month_data()


async def find_new_anime_today() -> None:

    # scheduler.add_job(find_ongoing, "interval", seconds=5)
    # scheduler.add_job(analitic_user_data, 'cron', day_of_week='mon-sun', hour=23, minute=00)
    # scheduler.start()
    
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        create_push_model = PushAnimeToday()

        while True:
            await asyncio.sleep(randrange(150, 250))
            # await asyncio.sleep(10)

            headers = {
                    "User-Agent" : UserAgent().random, 
                    "Keep-Alive": str(randrange(60, 100)),
                    "Connection": "keep-alive"
                    }

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
        day_now = (datetime.now() + timedelta(hours=server_time)).day

        try:
            if isinstance(el, element.NavigableString):
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

    find_anime = AnimeToday(anime_name, series_num, voice_acting, page, search_key, anime_eng_name)

    if find_anime.anime_id not in query_db.db_list:

        for series in series_num.value:
            ser_num = SeriesNumberToday(series, search_key)

            voice_list = voice_acting.value.get(ser_num.value)
                       
            for voice in voice_list:
                if voice != "":
                    voice_act = VoiceActingToday(voice, search_key)
                    find_anime = AnimeToday(anime_name, ser_num, voice_act, page, search_key, anime_eng_name)
                    query_db.add_new_record(find_anime)


async def add_animego(el: BeautifulSoup, search_key: str,  query_db: QueryAnimeToday, session: aiohttp.ClientSession) -> None:

    anime_name = NameFindAnimeToday(el, search_key)
    series_num = SeriesNumberToday(el, search_key)
    voice_acting = VoiceActingToday(el, search_key)
    page = PageAnimeToday(el, search_key)

    headers = {"User-Agent" : UserAgent().random, 
            "Keep-Alive": str(randrange(60, 100)),
            "Connection": "keep-alive"
            }

    find_anime = AnimeToday(anime_name, series_num, voice_acting, page, search_key, anime_name)

    if query_db.query_animeid(find_anime):

        async with session.get(page.value, headers=headers) as resp: #need optimization

            if resp.status == 200:
                soup = BeautifulSoup(await resp.text(), "lxml")
                anime_eng_name = EngNameAnimeToday(soup, search_key)

                find_anime = AnimeToday(anime_name, series_num, voice_acting, page, search_key, anime_eng_name)

                query_db.add_new_record(find_anime)

    return "stop"


async def add_hdrezka(el: BeautifulSoup, search_key: str,  query_db: QueryAnimeToday, session: aiohttp.ClientSession) -> None:

    anime_name = NameFindAnimeToday(el, search_key)
    series_num = SeriesNumberToday(el, search_key)
    voice_acting = VoiceActingToday(el, search_key)
    page = PageAnimeToday(el, search_key)
    anime_eng_name = EngNameAnimeToday(el, search_key)

    find_anime = AnimeToday(anime_name, series_num, voice_acting, page, search_key, anime_eng_name)

    if query_db.query_animeid(find_anime):
        query_db.add_new_record(find_anime)

    return "stop"
            

    


SITE_FUNC_DICT = {"animego" : add_animego, "anitube" : add_anitube, "hdrezka" : add_hdrezka}


