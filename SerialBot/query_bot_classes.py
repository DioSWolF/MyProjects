#!/usr/bin/env python
# -*- coding: utf-8 -*-


import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from telebot.types import CallbackQuery, Message

from mymodels import AnimeDB, FindAnimeBD, UserInfoDB, UserToAnimeDB, session_db

from parse_classes import Anime, FindText, InfoUser
from parse_classes import IdUser, IdUserChat, UserLogin, UserFistName, IsBot, UserLanguage, UserPremium, InfoUser
from parse_classes import EngTitleAnime, RusTitleAnime, PageAnime, ImageAnime

from bot_token import bot, bot_id, save_image_folder
from search_dicts import SEARCH_SITE_INFO_DICT
from fake_useragent import UserAgent
from sqlalchemy.orm import joinedload

from random_word import RandomWords


class QueryUserInfo():
    session = session_db
    user_info_model = UserInfoDB


    def __init__(self, message: CallbackQuery) -> None:
        self.message = message


    def _parse_user_info(self) -> None:

        user_id = IdUser(self.message).value
        chat_id = IdUserChat(self.message).value
        user_login = UserLogin(self.message).value
        user_name = UserFistName(self.message).value
        user_is_bot = IsBot(self.message).value
        user_lang = UserLanguage(self.message).value
        user_prem = UserPremium(self.message).value
        
        user_info = InfoUser(user_id, chat_id, user_login, user_name, user_is_bot, user_lang, user_prem)

        self.parse_user = user_info


    def _add_user_info(self) -> None:

        user_query = self.session.query(self.user_info_model).filter_by(user_id=self.parse_user.user_id).first()

        if user_query == None and self.parse_user.user_id != bot_id:

            self.user_info = self.user_info_model(user_id=self.parse_user.user_id, chat_id=self.parse_user.chat_id, user_login=self.parse_user.user_login, \
                                user_name=self.parse_user.user_name, is_bot=self.parse_user.is_bot, language_code=self.parse_user.language_code,\
                                is_premium=self.parse_user.is_premium)

            self.session.add(self.user_info)
            self.session.commit()


    def add_new_user(self) -> None:
        self._parse_user_info()
        self._add_user_info()


    def get_user(self) -> UserInfoDB:
        chat_id = IdUserChat(self.message).value
        self.user_info = self.session.query(self.user_info_model).filter_by(chat_id=chat_id).first()
        return self.user_info


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
        image_path = self.image_path + self.search_key + "/"
        self.anime_info = self.anime_model(eng_title=self.parse_anime.eng_title, rus_title=self.parse_anime.rus_title,  \
                            anime_page=self.parse_anime.page, image_page=self.parse_anime.image.page, \
                            image_name=self.parse_anime.image.name, image_path=image_path, anime_site_link=self.search_key
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

                async with aiofiles.open(image_path, 'wb') as f:
                    await f.write(await resp.read())
            self.session.query(self.anime_model).filter_by(eng_title=self.parse_anime.eng_title).update({self.anime_model.image_name : self.parse_anime.image.name}, synchronize_session=False)
            self.session.commit()
        

    async def _add_new_anime(self) -> None:
        for element in self.soup.select(".animes-grid-item"):
            self._parse_new_anime(element)
            self.anime_info = self.session.query(self.anime_model).filter_by(eng_title=self.parse_anime.eng_title).first()

            if self.anime_info == None:
                self._add_anime_bd()
                await self._save_image()
            self._add_user_anime_find()


    async def find_anime(self, message: CallbackQuery, user_info: UserInfoDB, search_key: str ="animego") -> None:
        self.message = message
        self.user_info = user_info
        self.search_key = search_key
        self._delete_pagin_anime()

        page_list = 1
        stop = []

        async with self.client_session_model() as self.client_session:

            find_text = self.find_text_model(self.message).value
            for self.search_key, site_page in SEARCH_SITE_INFO_DICT.items():
                while stop == []:

                    self.headers = {"User-Agent": self.fake_agent_model().random}

                    find_link = f"{site_page['link']}{find_text}{site_page['page_list']}{page_list}"

                    async with self.client_session.get(find_link, headers=self.headers) as resp: 
        
                        self.soup = self.bs_soup_model(await resp.text(), "lxml")
                        await self._add_new_anime()
                        stop = self.soup.select(site_page["stop_parse"])

                    page_list += 1

    
    async def find_random_anime(self, message: Message = None, user_info: UserInfoDB = None) -> None:

        if message != None and user_info != None:
            self.message = message
            self.user_info = user_info

        rand_word = RandomWords()
        self.message.text = rand_word.get_random_word()[0:3]

        await self.find_anime(self.message, self.user_info)


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):

        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)

        return class_._instance


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
        self.data[user_info.user_id] = user_info_query.anime_list_t


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


class MessageDeleteId(Singleton):
    data = {}
    pagin_data = {}
    pagin_data_save = {}


    def add_message_id(self, user_info: UserInfoDB, message: Message) -> None:
        
        if user_info.user_id not in self.data:
            self.data[user_info.user_id] = [message]
        elif isinstance(message, list):
            self.data[user_info.user_id].extend(message)
        else:
            self.data[user_info.user_id].append(message)


    def message_list(self, user_info: UserInfoDB) -> list[Message]:
        return self.data[user_info.user_id]
        

    async def delete_message_list(self, user_info: UserInfoDB) -> None:
        if user_info.user_id in self.data:
            for mes_id in self.data[user_info.chat_id]:  

                try:
                    await bot.delete_message(chat_id=user_info.chat_id, message_id=mes_id.message_id)

                except:
                    pass
            self.data[user_info.chat_id] = []


    async def safe_message_delete(self, user_info: UserInfoDB, message: Message) -> None:
        try:
            await bot.delete_message(chat_id=user_info.chat_id, message_id=message.message_id)
        except:
            pass
    

    async def special_delete(self, user_info: UserInfoDB, start_num: int = 0, end_num: int = -1) -> None:
        if user_info.user_id in self.data:
            for mes_id in self.data[user_info.chat_id][start_num : end_num]:  
                try:
                    await bot.delete_message(chat_id=user_info.chat_id, message_id=mes_id.message_id)
                    index_mes = self.data[user_info.chat_id].index(mes_id)
                    self.data[user_info.chat_id].pop(index_mes)
                except:
                    pass


    def add_pagin_mes_id(self, user_info: UserInfoDB, message: Message) -> None:
        if user_info.user_id not in self.pagin_data:
            self.pagin_data[user_info.user_id] = [message]
        else:
            self.pagin_data[user_info.user_id].append(message)
    

    async def delete_pagin_mes_list(self, user_info: UserInfoDB) -> None:
        for mes_id in self.pagin_data[user_info.chat_id]:  
            try:
                await bot.delete_message(chat_id=user_info.chat_id, message_id=mes_id.message_id)
                index_mes = self.pagin_data[user_info.chat_id].index(mes_id)
                self.pagin_data[user_info.chat_id].pop(index_mes)
            except:
                pass


    def add_save_pg_mes_id(self, user_info: UserInfoDB, message: Message) -> None:
        # if user_info.user_id not in self.pagin_data_save:
            self.pagin_data_save[user_info.user_id] = message

        # else:
        #     self.pagin_data_save[user_info.user_id].append(message)


    async def del_pg_save_mes(self, user_info: UserInfoDB) -> None:
        try:
            await bot.delete_message(chat_id=user_info.chat_id, message_id=self.pagin_data_save[user_info.chat_id].message_id)

            index = self.pagin_data[user_info.chat_id].index(self.pagin_data_save[user_info.chat_id])
            self.pagin_data[user_info.chat_id].pop(index)

        except:
            pass