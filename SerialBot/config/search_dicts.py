#!/usr/bin/env python
# -*- coding: utf-8 -*-


SITE_FLAG = {"anitube":"🇺🇦", "animego":"🏳🇷🇺🏳"}


SEARCH_SITE_DICT = {"animego" : {"link" : "https://animego.org", "page_list" : ""},
                    "anitube" : {"link" : "https://anitube.in.ua/anime/", "page_list" : "page/"}
                    }


SEARCH_SITE_INFO_DICT = {"animego": {"link" : "https://animego.org/search/anime?q=", 
                                    "page_list" : "&type=list&page=", 
                                    "stop_parse" : ".alert-warning", 
                                    "select" : ".animes-grid-item"},

                        "anitube" : {"link" : "https://anitube.in.ua/f/l.title=", 
                                    "page_list" : "/sort=date/order=desc/page/", 
                                    "stop_parse" : ".info_c", 
                                    "select" : ".story"}
                        }


SEARCH_TAGS_TODAY_DICT = {"animego" : {"find_soup" : "#slide-toggle-1"}, 
                        "anitube" : {"find_soup" : "#dle-content"}
                            }


FOLDERS_CREATE_DICT = {"./" : ["save_image"],
                        "./save_image/" : ["animego", "anitube"], 
                        }
