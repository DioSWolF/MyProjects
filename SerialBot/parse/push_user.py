#!/usr/bin/env python
# -*- coding: utf-8 -*-


from abc import ABC, abstractclassmethod
from datetime import datetime, timedelta
from re import findall
from config.bot_token import server_time
from config.search_dicts import SEARCH_SITE_DICT


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


class DateUpdate(AnimeTodayValue):

    @property
    def value(self) -> str:
        return self.__value


    @value.setter
    def value(self, value) -> str: 

        if self.search_key == "animego":
            value = (datetime.now() + timedelta(hours=server_time)).day

        if self.search_key == "anitube":
            value = int(value.select_one(".story_date sup").text)

        if self.search_key == "hdrezka":
            value = (datetime.now() + timedelta(hours=server_time)).day

        self.__value = value


class NameFindAnimeToday(AnimeTodayValue): 

    @property
    def value(self) -> str:
        return self.__value
    

    @value.setter
    def value(self, value) -> str: 

        if self.search_key == "animego":
            value = value.select_one(".last-update-title, font-weight-600").text

        if self.search_key == "anitube":
            value = value.select_one("h2 a").text

        if self.search_key == "hdrezka":
            # value = value.select_one(".b-seriesupdate__block_list_link").text 
            value = " "
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

        if self.search_key == "hdrezka":
            value = value.select_one(".b-seriesupdate__block_list_link").text 
            # try:
            #     value = value.select_one(".b-post__origtitle").text
            # except AttributeError:
            #     value = value.select_one(".b-post__title").text
            
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
            if isinstance(value, str):
                value = value.strip()

            else:    
                value = value.select_one(".story_link a").text
                value = findall(r" [0-9]+-[0-9]+ | [0-9]+ ", value)
                value.append("Перегляд")

                if value == []:
                    value = ""

        if self.search_key == "hdrezka":
            replace_ls = "(", ")"
            season = value.select_one(".season").text

            for item in replace_ls:
                season = season.replace(item, "")

            num = value.select_one(".cell-2").text.split("(")[0].strip()
            value = season + " " + num

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
            if isinstance(value, str):
                value = value

            else:  
                value = value.select_one(".story_link a").text
                value = self._anitube_voise_parse(value)

        if self.search_key == "hdrezka":
            replace_ls = "(", ")"
            value = value.select_one(".cell-2").select_one("i")

            if value == None:
                value = "Оригинал русский"

            else: 
                value = value.text

                for item in replace_ls:
                    value = value.replace(item, "")

        self.__value = value


    def _anitube_voise_parse(self, value) -> dict:
        repl_list = "\\", "/", ";", 
        for item in repl_list:
            value = value.replace(item, "|")

        clean_list = "серія", "Серія", "(", ")", 
        for it in clean_list:
            value = value.replace(it, "")

        value = value.split("|")

        num_list = []

        for it in value:
            serial_num = findall(r" [0-9]+-[0-9]+ | [0-9]+ ", it)

            if serial_num != []:
                num_list.append(serial_num[0].strip())

            num_list.append(it.strip())

        voise_dict = {"Перегляд" : []}

        for item in num_list:

            if item.replace("-", "").isdigit():
                key_num = item

                if key_num not in voise_dict:
                    voise_dict[item] = []

            else:
                try:
                    voise_dict[key_num].append(item)

                except UnboundLocalError:
                    voise_dict["Перегляд"].append(item)

        return voise_dict


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

            value = self.search_site_model["link"] + value

        if self.search_key == "anitube":
            value = value.select_one(".story_link, a").get('href')

        if self.search_key == "hdrezka":
            value = value.select_one(".b-seriesupdate__block_list_link").get("href")
            value = self.search_site_model["link"] + value

        self.__value = value


class AnimeToday:

    def __init__(self, name, series_number, voice_acting, page, search_key, eng_name) -> None:
        self.name: NameFindAnimeToday = name
        self.eng_name: EngNameAnimeToday = eng_name
        self.series_number: SeriesNumberToday = series_number
        self.voice_acting: VoiceActingToday = voice_acting
        self.page: PageAnimeToday = page
        self.search_key: str = search_key
        self.anime_id: str = f"{self.eng_name.value}|{self.name.value}|{self.series_number.value}|{self.voice_acting.value}|{self.search_key}"
        self.date_now: datetime = (datetime.now() + timedelta(hours=server_time)).date()
       
