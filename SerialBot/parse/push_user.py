#!/usr/bin/env python
# -*- coding: utf-8 -*-


from abc import ABC, abstractclassmethod
from datetime import datetime, timedelta
from re import findall

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
            value = datetime.now().day

        if self.search_key == "anitube":
            value = int(value.select_one(".story_date sup").text)

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
            if isinstance(value, str):
                value = value.strip()

            else:    
                value = value.select_one(".story_link a").text
                value = findall(r" [0-9]+-[0-9]+ | [0-9]+ ", value)
                value.append("Перегляд")

                if value == []:
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
            if isinstance(value, str):
                value = value

            else:  
                value = value.select_one(".story_link a").text
                
                value = self._anitube_voise_parse(value)

        self.__value = value


    def _anitube_voise_parse(self, value) -> dict:
        repl_list = "\\", "/", ";", 
        for item in repl_list:
            value = value.replace(item, "|")

        clean_list = "серія", "Серія", "(", ")"
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
       
