import logging
import multiprocessing
import os.path
import shutil

from db_storage import DBStorage
from hash_funcs import get_hash_of_file
from language_storage import LanguageStorage, LangStringEnum


class Storage:
    def __init__(self, directories_paths: list[str],
                 backup_directory: str,
                 language_storage: LanguageStorage,
                 max_directory_in_time_limit: int = 4):
        self.__db_storage = DBStorage()

        self.__directories_paths = directories_paths
        self.__backup_directory = backup_directory
        self.__language_storage = language_storage

        self.__locks = dict()

        self.__init_logger()

    @staticmethod
    def __init_logger():
        logging.basicConfig(level=logging.INFO,
                            filename="logs.log",
                            filemode="w",
                            format='(%(asctime)s) [%(levelname)s]: %(message)s')

    def scan_directories(self):
        for directory_path in self.__directories_paths:
            directory_lock = self.__locks.setdefault(directory_path, multiprocessing.Lock())

            multiprocessing.Process(target=self.__scan_directory,
                                    args=(directory_path, directory_lock)).start()
            multiprocessing.Process(target=self.__scan_directory_for_deleted_files,
                                    args=(directory_path,)).start()

    def __scan_directory(self, directory_path: str, lock: multiprocessing.Lock) -> None:
        lock.acquire()

        logging.info(self.__language_storage.get(LangStringEnum.StartDirectoryScanning,
                                                 directory_path=directory_path))

        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)

            if os.path.isfile(file_path):
                self.__scan_file(directory_path, file_path)

        lock.release()

    def __scan_directory_for_deleted_files(self, directory_path: str) -> None:
        files_list = self.__db_storage.get_files_list(directory_path)

        for file_path in files_list:
            if not os.path.exists(file_path):
                logging.info(self.__language_storage.get(LangStringEnum.FileRemoved,
                                                         file_path=file_path))

                if self.__exists_in_backup_directory(directory_path, file_path):
                    os.remove(self.get_file_path_in_backup(directory_path, file_path))
                    self.__db_storage.remove_file(file_path)

    def __scan_file(self, directory_path: str, file_path: str) -> None:
        if self.__db_storage.is_file_exists(file_path):
            self.__process_file_if_exists_in_db(directory_path, file_path)
        else:
            self.__process_file_if_not_exists_in_db(directory_path, file_path)

    def __get_backup_directory_path(self, directory_path: str):
        directory_name = os.path.split(os.path.dirname(directory_path))[-1]

        directory_backup_folder_path = os.path.join(self.__backup_directory, directory_name)

        return directory_backup_folder_path

    def __copy_file(self, directory_path: str, file_path: str):
        directory_backup_folder_path = self.__get_backup_directory_path(directory_path)

        if not os.path.exists(directory_backup_folder_path):
            os.makedirs(directory_backup_folder_path)

        shutil.copy(file_path, directory_backup_folder_path)

    def __process_file_if_exists_in_db(self, directory_path: str, file_path: str):
        logging.info(self.__language_storage.get(LangStringEnum.FileAlreadyExistsInDB,
                                                 file_path=file_path))

        if not self.__exists_in_backup_directory(directory_path, file_path):
            logging.info(self.__language_storage.get(LangStringEnum.FileNotExistsInDB,
                                                     file_path=file_path))
        elif not self.__compare_file_hash(directory_path, file_path):
            logging.info(self.__language_storage.get(LangStringEnum.FileHashHasChanged,
                                                     file_path=file_path))

            self.__copy_file(directory_path, file_path)
        else:
            return

        file_hash = get_hash_of_file(file_path)

        self.__db_storage.update_record(directory_path, file_path, file_hash)

    def __process_file_if_not_exists_in_db(self, directory_path: str, file_path: str):
        logging.info(self.__language_storage.get(LangStringEnum.FileNotExistsInDB,
                                                 file_path=file_path))

        file_hash = get_hash_of_file(file_path)

        self.__db_storage.update_record(directory_path, file_path, file_hash)

        self.__copy_file(directory_path, file_path)

    @staticmethod
    def __get_file_name_from_path(file_path: str) -> str:
        return os.path.basename(file_path)

    def __exists_in_backup_directory(self, directory_path: str, file_path: str) -> bool:
        file_backup_path = os.path.join(self.__get_backup_directory_path(directory_path),
                                        self.__get_file_name_from_path(file_path))

        return os.path.exists(file_backup_path)

    def __compare_file_hash(self, directory_path: str, file_path: str):
        hash_from_db = self.__db_storage.get_hash_of_file(file_path)
        hash_from_src = get_hash_of_file(file_path)

        file_backup_path = self.get_file_path_in_backup(directory_path, file_path)

        file_backup_hash = get_hash_of_file(file_backup_path)

        return not (hash_from_db != hash_from_src != file_backup_hash)

    def get_file_path_in_backup(self, directory_path: str, file_path: str) -> str:
        return os.path.join(self.__get_backup_directory_path(directory_path),
                            self.__get_file_name_from_path(file_path))
