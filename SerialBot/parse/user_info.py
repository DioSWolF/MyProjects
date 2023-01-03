#!/usr/bin/env python
# -*- coding: utf-8 -*-


from abc import ABC, abstractclassmethod
from telebot.types import Message


class ValueUser(ABC):

    def __init__(self, value: Message) -> None:
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
