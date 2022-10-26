#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import UserDict
import pickle
from all_classes import Anime, InfoChat, InfoUser
from abc import ABC, abstractclassmethod


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

        try:

            with open(".\\save_bin_file\\image_dict.bin", "rb") as file:
                self.data = pickle.load(file)
                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\image_dict.bin", "wb") as file:
                pickle.dump("", file)

            with open(".\\save_bin_file\\image_dict.bin", "rb") as file:
                return 


class AnimeToChatIdDict(Singleton, UserDict, SaveData):

    def add_data(self, anime: Anime, info_chat: InfoChat) -> None:

        self.load_data()

        if info_chat.chat_id.value not in self.data.keys():
            self.data[info_chat.chat_id.value] = {"info_chat" : info_chat, "anime_list" : [anime]}

        for anime_obj in self.data[info_chat.chat_id.value]["anime_list"]:

            if anime_obj.eng_title.value == anime.eng_title.value:
                return  self.save_data() 
            
        else:
            self.data[info_chat.chat_id.value]["anime_list"].append(anime)

        self.save_data()


    def delete_anime_in_chatid(self, anime: Anime, info_chat: InfoChat) -> None:
        self.load_data()

        for anime_in_chatid in self.data[info_chat.chat_id.value]["anime_list"]:

            if anime_in_chatid.eng_title.value == anime.eng_title.value:

                index_anime = self.data[info_chat.chat_id.value]["anime_list"].index(anime_in_chatid)
                self.data[info_chat.chat_id.value]["anime_list"].pop(index_anime)

        self.save_data()


    def save_data(self) -> None:

        with open(".\\save_bin_file\\anime_chatid.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:

        try:

            with open(".\\save_bin_file\\anime_chatid.bin", "rb") as file:
                self.data = pickle.load(file)

                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\anime_chatid.bin", "wb") as file:
                pickle.dump("", file)

            with open(".\\save_bin_file\\anime_chatid.bin", "rb") as file:
                return 


class ChatIdToAnimeDict(Singleton, UserDict, SaveData):

    def add_data(self, anime: Anime, info_chat: InfoChat) -> None:
            self.load_data()

            if anime.eng_title.value not in self.data.keys():
                self.data[anime.eng_title.value] = {"anime_info" : anime, "info_chat" : [info_chat]}

            for id_chat in self.data[anime.eng_title.value]["info_chat"]:
                if info_chat.chat_id.value == id_chat.chat_id.value:
                    return self.save_data()

            else:
                self.data[anime.eng_title.value]["info_chat"].append(info_chat)

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

        try:

            with open(".\\save_bin_file\\chatid_anime.bin", "rb") as file:
                self.data = pickle.load(file)

                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\chatid_anime.bin", "wb") as file:
                pickle.dump("", file)

            with open(".\\save_bin_file\\chatid_anime.bin", "rb") as file:
                return 


class InfoUserDict(Singleton, UserDict, SaveData):

    def add_data(self, user_info: InfoUser) -> None:
        if user_info.user_id.value != 5604497270:
            
            self.load_data()

            self.data[user_info.chat_id.value] = user_info

            self.save_data()


    def save_data(self) -> None:

        with open(".\\save_bin_file\\info_users.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:

        try:

            with open(".\\save_bin_file\\info_users.bin", "rb") as file:
                self.data = pickle.load(file)

                return self.data 

        except FileNotFoundError:

            with open(".\\save_bin_file\\info_users.bin", "wb") as file:
                pickle.dump("", file)

            with open(".\\save_bin_file\\info_users.bin", "rb") as file:
                return 