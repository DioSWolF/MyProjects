#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import UserDict
from datetime import datetime
import os
import pickle
from all_classes import Anime, InfoChat, InfoUser, AnimeToday
from abc import ABC, abstractclassmethod
from bot_token import bot_id

class SaveData(ABC):

    @abstractclassmethod
    def add_data(self):
        pass


    @abstractclassmethod
    def save_data(self):
        pass


    @abstractclassmethod
    def load_data(self):
        pass


class Singleton(object):
    _instance = None


    def __new__(class_, *args, **kwargs):

        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)

        return class_._instance


class ImageAnimeDict(Singleton, UserDict, SaveData):

    def add_data(self, anime: Anime) -> None:

        self.load_data()

        self.data[anime.image.page] = anime.image

        self.save_data()


    def save_data(self) -> None:

        with open(".\\save_bin_file\\image_dict.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:
        if os.path.exists(r".\\image") == False:
            os.mkdir(r".\\image")
        if os.path.exists(r".\\save_bin_file") == False:
            os.mkdir(r".\\save_bin_file")
        try:

            with open(".\\save_bin_file\\image_dict.bin", "rb") as file:
                self.data = pickle.load(file)
                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\image_dict.bin", "wb") as file:
                pickle.dump(self.data , file)

            with open(".\\save_bin_file\\image_dict.bin", "rb") as file:
                return self.data 


class AnimeToChatIdDict(Singleton, UserDict, SaveData):

    def add_data(self, anime: Anime, user: InfoChat) -> None:

        self.load_data()

        if user.user_id.value not in self.data.keys():
            self.data[user.user_id.value] = {"info_chat" : user, "anime_list" : [anime]}

        for anime_obj in self.data[user.user_id.value]["anime_list"]:

            if anime_obj.eng_title.value == anime.eng_title.value:
                return  self.save_data() 
            
        else:
            self.data[user.user_id.value]["anime_list"].append(anime)

        self.save_data()


    def delete_anime_in_chatid(self, anime: Anime, user: InfoUser) -> None:
        self.load_data()

        for anime_in_chatid in self.data[user.user_id.value]["anime_list"]:

            if anime_in_chatid.eng_title.value == anime.eng_title.value:

                index_anime = self.data[user.user_id.value]["anime_list"].index(anime_in_chatid)
                self.data[user.user_id.value]["anime_list"].pop(index_anime)

        self.save_data()


    def save_data(self) -> None:

        with open(".\\save_bin_file\\anime_chatid.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:
        if os.path.exists(r".\\save_bin_file") == False:
            os.mkdir(r".\\save_bin_file")
        try:

            with open(".\\save_bin_file\\anime_chatid.bin", "rb") as file:
                self.data = pickle.load(file)

                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\anime_chatid.bin", "wb") as file:
                pickle.dump(self.data , file)

            with open(".\\save_bin_file\\anime_chatid.bin", "rb") as file:
                return self.data 


class ChatIdToAnimeDict(Singleton, UserDict, SaveData):

    def add_data(self, anime: Anime, user: InfoUser) -> None:
        self.load_data()
        
        if anime.eng_title.value not in self.data.keys():
            self.data[anime.eng_title.value] = {"anime_info" : anime, "info_chat" : [user]}

        for id_chat in self.data[anime.eng_title.value]["info_chat"]:
            if user.user_id.value == id_chat.user_id.value:
                return self.save_data()

        else:
            self.data[anime.eng_title.value]["info_chat"].append(user)

        self.save_data()


    def delete_chatid_in_anime(self, anime: Anime, info_chat: InfoChat) -> None:
        self.load_data()

        for chat_in_anime in self.data[anime.eng_title.value]["info_chat"]:

            if chat_in_anime.chat_id.value == info_chat.chat_id.value:

                index_chatid = self.data[anime.eng_title.value]["info_chat"].index(chat_in_anime)
                self.data[anime.eng_title.value]["info_chat"].pop(index_chatid)

        self.save_data()


    def save_data(self) -> None:

        with open(".\\save_bin_file\\chatid_anime.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:
        if os.path.exists(r".\\save_bin_file") == False:
            os.mkdir(r".\\save_bin_file")
        try:

            with open(".\\save_bin_file\\chatid_anime.bin", "rb") as file:
                self.data = pickle.load(file)

                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\chatid_anime.bin", "wb") as file:
                pickle.dump(self.data, file)

            with open(".\\save_bin_file\\chatid_anime.bin", "rb") as file:
                return self.data 


class InfoUserDict(Singleton, UserDict, SaveData):

    def add_data(self, user_info: InfoUser) -> None:

        if user_info.user_id.value != bot_id:
    
            self.load_data()

            self.data[user_info.chat_id.value] = user_info

            self.save_data()


    def save_data(self) -> None:

        with open(".\\save_bin_file\\info_users.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:
        if os.path.exists(r".\\save_bin_file") == False:
            os.mkdir(r".\\save_bin_file")
        try:

            with open(".\\save_bin_file\\info_users.bin", "rb") as file:
                self.data = pickle.load(file)

                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\info_users.bin", "wb") as file:
                pickle.dump(self.data , file)

            with open(".\\save_bin_file\\info_users.bin", "rb") as file:
                return self.data 


class AnimeFindToday(Singleton, UserDict, SaveData):

    async def add_data(self, anime_today_list: list[AnimeToday], anime: dict[Anime]) -> None:
        
        self.load_data()

        self.data["time_date"] = datetime.now().date()

        for anime_today in anime_today_list:
            for anime_item in anime.values():
                if anime_today.name.value == anime_item["anime_info"].rus_title.value:
                    save_key = f"{anime_today.name.value}|{anime_today.series_number.value}|{anime_today.voice_acting.value}"
                    if save_key not in self.data:
                        self.data[save_key] = {"anime_today" : anime_today, "anime" : anime_item["anime_info"], "push_flag" : False}

        self.save_data()


    def change_push_flag(self, anime_today: AnimeToday, flag: bool = True):

        self.load_data()

        save_key = f"{anime_today.name.value}|{anime_today.series_number.value}|{anime_today.voice_acting.value}"
        self.data[save_key]["push_flag"] = flag

        self.save_data()
        return self.data


    def clean_data(self):

        self.load_data()

        if self.data["time_date"] != datetime.now().date():
            self.data.clear()

        self.data["time_date"] = datetime.now().date()

        self.save_data()


    def save_data(self) -> None:

        with open(".\\save_bin_file\\find_today.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:
        if os.path.exists(r".\\save_bin_file") == False:
            os.mkdir(r".\\save_bin_file")
        try:
            with open(".\\save_bin_file\\find_today.bin", "rb") as file:
                self.data = pickle.load(file)
                return self.data 

        except FileNotFoundError:
            with open(".\\save_bin_file\\find_today.bin", "wb") as file:
                pickle.dump(self.data , file)

            with open(".\\save_bin_file\\find_today.bin", "rb") as file:
                return self.data 


