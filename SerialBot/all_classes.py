#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import UserList
from abc import ABC, abstractclassmethod
import telebot.async_telebot
from bs4 import BeautifulSoup
import uuid


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ find anime classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ValueAnime(ABC):

    def __init__(self, value: BeautifulSoup|telebot.async_telebot.types.CallbackQuery = None) -> None:
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


class FindText(ValueAnime):
    
    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.text.strip().replace(" ", "%20")


class EngTitleAnime(ValueAnime):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.select_one(".text-gray-dark-6").text


class RusTitleAnime(ValueAnime):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str:
        self.__value = value.select_one(".h5").select_one("a").get("title")


class PageAnime(ValueAnime):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.select_one(".h5").select_one("a").get("href")


class SeriesNumber(ValueAnime):
    
    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        if value == None:
            self.__value = None
        else:
            self.__value = value # need to update


class ImageAnime():

    def __init__(self, image_name: BeautifulSoup) -> None:
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
        page = page.select_one(".anime-grid-lazy").get("data-original")
        self.__page = page


class Anime:
    find_flag = False

    def __init__(self, eng_title, rus_title, page, image, counter, series_number = None) -> None:
        self.eng_title: EngTitleAnime = eng_title
        self.rus_title: RusTitleAnime = rus_title
        self.page: PageAnime = page
        self.image: ImageAnime = image

        self.counter:int = counter

        self.series_number: SeriesNumber = series_number


class FindAnimeList(UserList):

    def add_data(self, anime: Anime) -> None:
        self.data.append(anime)


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


class JsonUserInfo(ValueUser):
    
    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.json


class InfoUser:

    def __init__(self, user_id, chat_id, user_login, user_name, is_bot, language_code, is_premium, json_info) -> None:
        self.user_id: IdUser = user_id
        self.chat_id: IdChat = chat_id
        self.user_login: UserLogin = user_login
        self.user_name: UserFistName = user_name
        self.is_bot: IsBot = is_bot
        self.language_code: UserLanguage = language_code
        self.is_premium: UserPremium = is_premium
        self.json_info: JsonUserInfo = json_info


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ chat id classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ValueChat(ABC):

    def __init__(self, value: telebot.async_telebot.types.CallbackQuery) -> None:
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


class IdChat(ValueChat):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.chat.id


class IdChatUser(ValueChat):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 
        self.__value = value.from_user.id


class ChatIdMessage(ValueChat):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value: telebot.async_telebot.types.CallbackQuery) -> str: 
        self.__value = value.message_id


class JsonChat(ValueChat):

    @property 
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value: telebot.async_telebot.types.CallbackQuery) -> str: 
        self.__value = value.json


class InfoChat:

    def __init__(self, chat_id: IdChat, message_id: ChatIdMessage, user_id: IdChatUser, json_chat: JsonChat) -> None:
        self.chat_id = chat_id
        self.message_id = message_id
        self.user_id = user_id
        self.json_chat = json_chat
        

