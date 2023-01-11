#!/usr/bin/env python
# -*- coding: utf-8 -*-


from abc import ABC, abstractclassmethod

from bs4 import BeautifulSoup

import uuid
from urllib.parse import quote

import telebot.async_telebot
from telebot.asyncio_handler_backends import State, StatesGroup

from config.search_dicts import SEARCH_SITE_DICT



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

        if self.search_key == "hdrezka":
            value = value.select_one(".b-content__inline_item-link a").text
            
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
            value = value.select_one("a, name").text

        if self.search_key == "hdrezka":
            # value = value.select_one(".b-content__inline_item-link a").text
            value = " "
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

        if self.search_key == "hdrezka":
            value = value.select_one("a").get("href")

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

        if self.search_key == "hdrezka":
            page = page.select_one("img").get("src")

        self.__page = page



class Anime:
    new_today = False

    def __init__(self, eng_title, rus_title, page, image) -> None:
        self.eng_title: EngTitleAnime = eng_title
        self.rus_title: RusTitleAnime = rus_title
        self.page: PageAnime = page
        self.image: ImageAnime = image
        
