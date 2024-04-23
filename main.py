import json
import time

from async_state import AsyncState
from language_storage import LanguageStorage, LangStringEnum
from storage import Storage


def start_periodic_task(storage: Storage,
                        interval_in_seconds: int,
                        running_flag: AsyncState) -> None:

    while running_flag.value:
        time.sleep(interval_in_seconds)

        storage.scan_directories()


def init_storage(directories_paths: list[str],
                 backup_directory: str,
                 language_storage: LanguageStorage) -> Storage:
    storage = Storage(directories_paths=directories_paths,
                      backup_directory=backup_directory,
                      language_storage=language_storage)

    return storage


def main() -> None:
    with open('config.json', 'r') as f:
        config_dict = json.load(f)

    language_storage = LanguageStorage(config_dict['language_path'])

    storage = init_storage(config_dict['directories_paths'],
                           config_dict['backup_directory_path'],
                           language_storage)

    interval_in_seconds = config_dict['interval_in_seconds']
    running_flag = AsyncState(value=True)

    try:
        print(language_storage.get(LangStringEnum.ServerStartMessage))

        start_periodic_task(storage,
                            interval_in_seconds,
                            running_flag)
    except (KeyboardInterrupt, ):
        running_flag.value = False

        print(language_storage.get(LangStringEnum.ServerStopMessage))


if __name__ == '__main__':
    main()
