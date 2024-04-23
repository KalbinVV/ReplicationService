import enum
import json


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


class LangStringEnum(enum.Enum):
    ServerStartMessage = 'server_start_message'
    ServerStopMessage = 'server_stop_message'
    StartDirectoryScanning = 'start_directory_scanning'
    FileAlreadyExistsInDB = 'file_already_exists_in_db'
    FileNotExistsInDB = 'file_not_exists_in_db'
    FileHashHasChanged = 'file_hash_has_changed'
    FileNotExistsInBackupDirectory = 'file_not_exists_in_backup_directory'
    FileRemoved = 'file_removed'


@singleton
class LanguageStorage:
    def __init__(self, file_path: str = 'lang.json'):
        with open(file_path, 'r') as f:
            self.__json_dict = json.load(f)

    def get(self, lang_string_enum: LangStringEnum, **args):
        return self.__json_dict[lang_string_enum.value].format(**args)
