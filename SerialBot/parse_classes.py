#!/usr/bin/env python
# -*- coding: utf-8 -*-


from abc import ABC, abstractclassmethod
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

import uuid
from urllib.parse import quote

import telebot.async_telebot
from telebot.asyncio_handler_backends import State, StatesGroup

from search_dicts import SEARCH_SITE_DICT


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ state classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MyStates(StatesGroup):
    find_text = State()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ find anime classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ValueAnime(ABC):

    def __init__(self, value: BeautifulSoup|telebot.async_telebot.types.CallbackQuery, search_key: str = None) -> None:
        self.search_key = search_key
        self.search_site_model = SEARCH_SITE_DICT[self.search_key]
        self.__value: str = ""
        self.value: str = value


    @property 
    @abstractclassmethod
    def value(self) -> str:
        pass


    @value.setter
    @abstractclassmethod
    def value(self, value) -> str: 
        pass


class FindText():
    def __init__(self, value) -> None:
        self.__value: str = ""
        self.value: str = value

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = quote(value.text.strip())


class EngTitleAnime(ValueAnime):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        if self.search_key == "animego":
            value = value.select_one(".text-gray-dark-6").text
        
        if self.search_key == "anitube":
            value = value.select_one("a, name").text

        self.__value = value


class RusTitleAnime(ValueAnime):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str:
        if self.search_key == "animego":
            value = value.select_one(".h5").select_one("a").get("title")

        if self.search_key == "anitube":
            value = ""

        self.__value = value


class PageAnime(ValueAnime):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        if self.search_key == "animego":
            value = value.select_one(".h5").select_one("a").get("href")
        if self.search_key == "anitube":
            value = value.select_one("a, name").get("href")
        self.__value = value


class ImageAnime():

    def __init__(self, image_name: BeautifulSoup, search_key: str) -> None:
        self.search_key = search_key
        self.__name: str = ""
        self.name: str = image_name
        self.__page: str = ""
        self.page: str = image_name


    @property
    def name(self) -> str:
        return self.__name


    @name.setter
    def name(self, name) -> str: 
        name = f"{uuid.uuid4()}.jpg"
        self.__name = name
        

    @property
    def page(self) -> str:
        return self.__page


    @page.setter
    def page(self, page) -> str: 
        if self.search_key == "animego":
            page = page.select_one(".anime-grid-lazy").get("data-original")

        if self.search_key == "anitube":
            page = page.select_one(".story_post img").get("src")
            page = "https://anitube.in.ua" + page

        self.__page = page



class Anime:
    new_today = False

    def __init__(self, eng_title, rus_title, page, image) -> None:
        self.eng_title: EngTitleAnime = eng_title
        self.rus_title: RusTitleAnime = rus_title
        self.page: PageAnime = page
        self.image: ImageAnime = image
        

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Anime today ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnimeTodayValue(ABC):
    def __init__(self, value, search_key = None) -> None:
        super().__init__()
        self.search_key = search_key
        self.search_site_model = SEARCH_SITE_DICT[self.search_key]
        self.__value: str = ""
        self.value: str = value


    @property 
    @abstractclassmethod
    def value(self) -> str:
        pass


    @value.setter
    @abstractclassmethod
    def value(self, value) -> str: 
        pass


class NameFindAnimeToday(AnimeTodayValue): 

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 

        if self.search_key == "animego":
            value = value.select_one(".last-update-title, font-weight-600").text

        if self.search_key == "anitube":
            value = ""

        self.__value = value


class EngNameAnimeToday(AnimeTodayValue):
    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 

        if self.search_key == "animego":
            value = value.select_one(".list-unstyled").find("li").text

        if self.search_key == "anitube":
            value = value.select_one("h2 a").text

        self.__value = value


class SeriesNumberToday(AnimeTodayValue): 
    
    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 

        if self.search_key == "animego":
            value = value.select_one(".ml-3").text
            value = value.split("(")[0]
            value = value.split()[0]

        if self.search_key == "anitube":
            value = ""

        self.__value = value


class VoiceActingToday(AnimeTodayValue): 

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 

        if self.search_key == "animego":
            value = value.select_one(".ml-3").text
            value = value.split("(")[1]
            value = value.replace(")", "")
            if value == "Субтитры":
                value = f"Subtitle|{value}"

        if self.search_key == "anitube":
            value = value.select_one(".story_link a").text

        self.__value = value


class PageAnimeToday(AnimeTodayValue):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 

        if self.search_key == "animego":
            replace_href = ["location.href=", "'"]
            value = value.attrs["onclick"]
            for item in replace_href:
                value = value.replace(item, "")
            value = self.search_site_model + value

        if self.search_key == "anitube":
            value = value.select_one(".story_link, a").get('href')

        self.__value = value


class AnimeToday:

    def __init__(self, name, eng_name, series_number, voice_acting, page, search_key) -> None:
        self.name: NameFindAnimeToday = name
        self.eng_name: EngNameAnimeToday = eng_name
        self.series_number: SeriesNumberToday = series_number
        self.voice_acting: VoiceActingToday = voice_acting
        self.page: PageAnimeToday = page
        self.search_key: str = search_key
        self.anime_id: str = f"{self.eng_name.value}|{self.series_number.value}|{self.voice_acting.value}|{self.search_key}"
        self.date_now: datetime = (datetime.now() + timedelta(hours=2)).date()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ User info ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ValueUser(ABC):

    def __init__(self, value: BeautifulSoup) -> None:
        self.__value: str = ""
        self.value: str = value


    @property 
    @abstractclassmethod
    def value(self) -> str:
        pass


    @value.setter
    @abstractclassmethod
    def value(self, value) -> str: 
        pass


class IdUser(ValueUser):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.from_user.id


class IdUserChat(ValueUser):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.chat.id


class UserLogin(ValueUser):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.from_user.username


class UserFistName(ValueUser):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.from_user.first_name


class IsBot(ValueUser):
    
    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> bool: 
        self.__value = value.from_user.is_bot


class UserLanguage(ValueUser):
    
    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.from_user.language_code


class UserPremium(ValueUser):
    
    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.from_user.is_premium


class InfoUser:

    def __init__(self, user_id, chat_id, user_login, user_name, is_bot, language_code, is_premium) -> None:
        self.user_id: IdUser = user_id
        self.chat_id: IdUserChat = chat_id
        self.user_login: UserLogin = user_login
        self.user_name: UserFistName = user_name
        self.is_bot: IsBot = is_bot
        self.language_code: UserLanguage = language_code
        self.is_premium: UserPremium = is_premium

