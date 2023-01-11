from os.path import exists
from os import mkdir
from config.search_dicts import FOLDERS_CREATE_DICT


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):

        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)

            for folder_path, folder in FOLDERS_CREATE_DICT.items():
                for fold in folder:
                    if not exists(folder_path + fold):
                        mkdir(folder_path + fold)

        return class_._instance


