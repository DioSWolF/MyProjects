#!/usr/bin/env python
# -*- coding: utf-8 -*-


SITE_FLAG = {"anitube":" 🇺🇦Anitube🇺🇦 ", "animego":" 🏳AnimeGo🏳 ", "hdrezka" : " 🇺🇦HDrezka 🇺🇦"}


BT_DICT = {f"{SITE_FLAG['animego']}" : "change_search_site#animego",  
            f"{SITE_FLAG['anitube']}" : "change_search_site#anitube",
            f"{SITE_FLAG['hdrezka']}" : "change_search_site#hdrezka", 
            "Back" : "back"
            }


SEARCH_SITE_DICT = {"animego" : {"link" : "https://animego.org", "page_list" : ""},
                    "anitube" : {"link" : "https://anitube.in.ua/anime/", "page_list" : "page/"},
                    "hdrezka" : {"link" : "https://rezka.ag/", "page_list" : ""},
                    }


SEARCH_SITE_INFO_DICT = {"animego": {"link" : "https://animego.org/search/anime?q=", 
                                    "page_list" : "&type=list&page=", 
                                    "stop_parse" : ".alert-warning", 
                                    "select" : ".animes-grid-item"},

                        "anitube" : {"link" : "https://anitube.in.ua/f/l.title=", 
                                    "page_list" : "/sort=date/order=desc/page/", 
                                    "stop_parse" : ".info_c", 
                                    "select" : ".story"},

                        "hdrezka" : {"link" : "https://rezka.ag/search/?do=search&subaction=search&q=", 
                                    "page_list" : "&page=", 
                                    "stop_parse" : ".b-info__message", 
                                    "select" : ".b-content__inline_item"},
                        }


ONGOING_LIST_FIND_DICT = {"animego" : {"link" : "https://animego.org/anime/status/ongoing", 
                                    "page_list" : "?sort=a.createdAt&direction=desc&type=animes&page=", 
                                    "select" : "#anime-list-container"}
                        }


SEARCH_TAGS_TODAY_DICT =    {"animego" : {"find_soup" : "#slide-toggle-1"}, 
                            "anitube" : {"find_soup" : "#dle-content"},
                            "hdrezka" : {"find_soup" : ".b-seriesupdate__block_list"},
                            }


FOLDERS_CREATE_DICT = {"path" : ["folder"],
                        "path 2" : ["folder 2"], 
                        "path" : ["animego", "anitube", "hdrezka"]
                        }



