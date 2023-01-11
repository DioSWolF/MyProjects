#!/usr/bin/env python
# -*- coding: utf-8 -*-


from random import randrange
from fake_useragent import UserAgent
import aiofiles
import aiohttp
from bs4 import BeautifulSoup, NavigableString
from sqlalchemy.orm import joinedload
from database.mymodels import AnimeDB, FindAnimeBD, UserInfoDB, UserToAnimeDB, session_db
from parse.find_anime import Anime, FindText, EngTitleAnime, RusTitleAnime, PageAnime, ImageAnime
from classes.singleton import Singleton
from telebot.types import CallbackQuery, Message
from config.bot_token import save_image_folder
from config.search_dicts import SEARCH_SITE_INFO_DICT
from random_word import RandomWords


class QueryAnime():
    anime_model = AnimeDB
    user_info_model = UserInfoDB
    pagin_anime_model = FindAnimeBD
    client_session_model = aiohttp.ClientSession
    bs_soup_model = BeautifulSoup
    find_text_model = FindText
    fake_agent_model = UserAgent

    session = session_db
    image_path = save_image_folder
    

    def _add_user_anime_find(self) -> None:
        pagin_anime = self.pagin_anime_model(user_id = self.user_info.user_id, anime_id=self.anime_info.anime_id) 
        self.session.add(pagin_anime)
        self.session.commit()


    def _delete_pagin_anime(self) -> None:
        self.session.query(self.pagin_anime_model).filter_by(user_id=self.user_info.user_id).delete()
        self.session.commit()

    def _parse_new_anime(self, element) -> None:
        
        eng_title = EngTitleAnime(element, self.search_key).value
        rus_title = RusTitleAnime(element, self.search_key).value
        page_anime = PageAnime(element, self.search_key).value
        image_anime = ImageAnime(element, self.search_key)

        self.parse_anime = Anime(eng_title, rus_title, page_anime, image_anime)


    def _add_anime_bd(self) -> None:
        
        self.anime_info = self.anime_model(eng_title=self.parse_anime.eng_title, rus_title=self.parse_anime.rus_title,  \
                            anime_page=self.parse_anime.page, image_page=self.parse_anime.image.page, \
                            image_name=self.parse_anime.image.name, anime_site_link=self.search_key
                            )

        self.session.add(self.anime_info)
        self.session.commit()


    async def _get_image(self) -> None:
        resp = await self.client_session.request(method="GET", headers = self.headers, url=self.parse_anime.image.page)
        return resp


    async def _save_image(self) -> None:
            
            resp = await self._get_image()

            if resp and resp.status == 200:

                image_path = self.image_path + self.search_key + "/" + self.parse_anime.image.name
                
                async with aiofiles.open(image_path, "wb") as f:

                    await f.write(await resp.read())

                    self.session.query(self.anime_model).filter_by(eng_title=self.parse_anime.eng_title).update({self.anime_model.image_name : self.parse_anime.image.name, self.anime_model.image_path : self.image_path + self.search_key + "/"}, synchronize_session=False)

            self.session.commit()
        

    async def _add_new_anime(self) -> None:
        
        for element in self.soup.select(self.s_dc_model["select"]):
            if isinstance(element, NavigableString): 
                break
            self._parse_new_anime(element)
            self.anime_info = self.session.query(self.anime_model).filter_by(eng_title=self.parse_anime.eng_title).first()

            if self.anime_info == None:
                self._add_anime_bd()
                await self._save_image()
            self._add_user_anime_find()


    async def find_anime(self, message: CallbackQuery, user_info: UserInfoDB) -> None:
        # start = datetime.now()

        self.message = message
        self.user_info = user_info
        self.search_key = user_info.chose_site
        self.s_dc_model = SEARCH_SITE_INFO_DICT[self.search_key]
        self._delete_pagin_anime()

        page_list = 1
        stop = []

        async with self.client_session_model() as self.client_session:

            find_text = self.find_text_model(self.message).value

            while True:

                self.headers = {"User-Agent" : UserAgent().random, 
                                "Keep-Alive": str(randrange(60, 100)),
                                "Connection": "keep-alive"
                                }

                find_link = f"{self.s_dc_model['link']}{find_text}{self.s_dc_model['page_list']}{page_list}"

                async with self.client_session.get(find_link, headers=self.headers) as resp: 

                    if resp.status == 200:
                        self.soup = self.bs_soup_model(await resp.text(), "lxml")
                        
                        stop = self.soup.select(self.s_dc_model["stop_parse"])

                        if stop != []:
                            # print(datetime.now() - start)
                            return

                        await self._add_new_anime()

                        page_list += 1
        
    
    async def find_random_anime(self, message: Message = None, user_info: UserInfoDB = None) -> None:

        if message != None and user_info != None:
            self.message = message
            self.user_info = user_info

        rand_word = RandomWords()
        self.message.text = rand_word.get_random_word()[0:3]

        await self.find_anime(self.message, self.user_info)
    

class AnimeToUser():
    session = session_db
    user_info_model = UserInfoDB
    anime_model = AnimeDB
    user_to_anime_model = UserToAnimeDB


    def add_anime_user(self, user_info: UserInfoDB, anime: AnimeDB) -> None:
        query_anime = self.session.query(self.user_to_anime_model).filter_by(user_id=user_info.user_id, anime_id=anime.anime_id).first()
        if query_anime == None:
            new_anime = self.user_to_anime_model(user_id = user_info.user_id, anime_id = anime.anime_id)
            self.session.add(new_anime)
            self.session.commit()


    def del_anime_user(self, user_info: UserInfoDB, anime: AnimeDB) -> None:
        self.session.query(self.user_to_anime_model).filter_by(user_id=user_info.user_id, anime_id=anime.anime_id).delete()
        self.session.commit()


class PaginFindAnime(Singleton):
    pagin_anime_model = FindAnimeBD
    user_info_model = UserInfoDB
    session = session_db
    data = {}
    number_pagin = {}

    
    def _find_anime_list(self, user_info: UserInfoDB) -> None:
        anime_list:UserInfoDB = self.session.query(self.user_info_model).options(joinedload("find_anime_t")).filter_by(user_id=user_info.user_id).first()
        self.data[user_info.user_id] = anime_list.find_anime_t


    def del_anime_in_pagin(self, user_info: UserInfoDB, anime: AnimeDB) -> None:
        self.session.query(self.pagin_anime_model).filter_by(user_id = user_info.user_id, anime_id = anime.anime_id).delete()
        self.session.commit()
        self._find_anime_list(user_info)


    def get_anime_list(self, user_info: UserInfoDB) -> list[AnimeDB]:
        self._find_anime_list(user_info)
        if user_info.user_id not in self.data:
            self.data[user_info.user_id] = []
            return self.data[user_info.user_id]

        return self.data[user_info.user_id]


    def add_num_pagin(self, user_info: UserInfoDB) -> None:
        if user_info.user_id not in self.number_pagin:
            self.number_pagin[user_info.user_id] = 0
    

    def dump_num(self, call: CallbackQuery, user_info: UserInfoDB, anime_pagin_dict: dict|list) -> int:
        dict_num = self.number_pagin[user_info.user_id]
        
        try:
            if call.data.split("|||")[0] == "back_page":
                dict_num -= 1

            elif call.data.split("|||")[0] == "next_page":
                dict_num += 1
        except:
            pass

        if dict_num > len(anime_pagin_dict) - 1:
            dict_num = len(anime_pagin_dict) - 1

        elif 0 > dict_num:
            dict_num = 0

        if dict_num == -1:
            dict_num = 0

        self.number_pagin[user_info.user_id] = dict_num

        return self.number_pagin[user_info.user_id]


    def get_pagin_anime_dict(self, user_info: UserInfoDB, num_list: int = 9) -> dict[int : [list[AnimeDB]]]:
        self._find_anime_list(user_info)
        pagin_dict = {}
        i = 1
        I = 0
        anim_list = []
        for anime in self.data[user_info.user_id]:
            anim_list.append(anime)
            if i == num_list:
                pagin_dict[I] = anim_list
                anim_list = []
                i = 0
                I += 1
            i += 1
        if anim_list != []:
            pagin_dict[len(pagin_dict)] = anim_list
            anim_list = []

        return pagin_dict


class ShowUserList(Singleton):
    session = session_db
    user_info_model = UserInfoDB
    anime_model = AnimeDB
    data = {}
    number_pagin = {}


    def _get_user_anime_list(self, user_info: UserInfoDB) -> list[AnimeDB]:
        user_info_query: UserInfoDB = self.session.query(self.user_info_model).filter_by(user_id=user_info.user_id).first()
        anime_ls = []
        
        for anime in user_info_query.anime_list_t:
            if anime.anime_site_link == user_info.chose_site:
                anime_ls.append(anime)

        self.data[user_info.user_id] = anime_ls[::-1]


    def get_anime_list(self, user_info: UserInfoDB) -> list[AnimeDB]:
        self._get_user_anime_list(user_info)

        if user_info.user_id not in self.data:
            self.data[user_info.user_id] = []
            return self.data[user_info.user_id]

        return self.data[user_info.user_id]
    

    def get_pagin_anime_dict(self, user_info: UserInfoDB, num_list: int = 9) -> dict[int : [list[AnimeDB]]]:
        self._get_user_anime_list(user_info)
        pagin_dict = {}
        i = 1
        I = 0
        anim_list = []
        for anime in self.data[user_info.user_id]:
            anim_list.append(anime)
            if i == num_list:
                pagin_dict[I] = anim_list
                anim_list = []
                i = 0
                I += 1
            i += 1
        if anim_list != []:
            pagin_dict[len(pagin_dict)] = anim_list
            anim_list = []

        return pagin_dict


    def add_pagin_num(self, user_info: UserInfoDB) -> None:
        if user_info.user_id not in self.number_pagin:
            self.number_pagin[user_info.user_id] = 0


    def dump_num(self, call: CallbackQuery, user_info: UserInfoDB, anime_pagin_dict: dict|list) -> int:
        dict_num = self.number_pagin[user_info.user_id]
        
        try:
            if call.data.split("|||")[0] == "back_page":
                dict_num -= 1

            elif call.data.split("|||")[0] == "next_page":
                dict_num += 1
        except:
            pass

        if dict_num > len(anime_pagin_dict) - 1:
            dict_num = len(anime_pagin_dict) - 1

        elif 0 > dict_num:
            dict_num = 0

        if dict_num == -1:
            dict_num = 0

        self.number_pagin[user_info.user_id] = dict_num

        return self.number_pagin[user_info.user_id]


