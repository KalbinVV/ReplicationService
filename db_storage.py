import sqlite3

from context_cursor import ContextCursor


class DBStorage:
    def __init__(self):
        self.__connection = sqlite3.connect('storage.db', check_same_thread=False)
        self.__init_tables()

    def __init_tables(self):
        create_table_sql = '''
            CREATE TABLE if not exists records(
                id integer PRIMARY KEY AUTOINCREMENT,
                directory_path text not NULL,
                file_path text not NULL,
                hash_value text not NULL
        );
        '''

        with ContextCursor(self.__connection) as cursor:
            cursor.execute(create_table_sql)

        self.__connection.commit()

    def is_file_exists(self, file_path: str) -> bool:
        file_count_sql = f'select count(*) from records where file_path = "{file_path}"'

        with ContextCursor(self.__connection) as cursor:
            file_count = cursor.execute(file_count_sql).fetchone()[0]

            return file_count > 0

    def update_record(self, directory_path: str, file_path: str, hash_value: str):
        if self.is_file_exists(file_path):
            update_record_sql = f'update records set directory_path = "{directory_path}",' \
                                f'hash_value = "{hash_value}" ' \
                                f'where file_path = "{file_path}"'

        else:
            update_record_sql = f'insert into records(directory_path, file_path, hash_value)' \
                                f'values("{directory_path}", "{file_path}", "{hash_value}")'

        with ContextCursor(self.__connection) as cursor:
            cursor.execute(update_record_sql)

        self.__connection.commit()

    def get_hash_of_file(self, file_path: str) -> str:
        get_hash_of_file_sql = f'select hash_value from records where file_path = "{file_path}"'

        with ContextCursor(self.__connection) as cursor:
            hash_value = cursor.execute(get_hash_of_file_sql).fetchone()[0]

            return hash_value

    def get_files_list(self, directory_path: str) -> list[str]:
        get_files_list_sql = f'select file_path from records where directory_path = "{directory_path}"'

        with ContextCursor(self.__connection) as cursor:
            return [row[0] for row in cursor.execute(get_files_list_sql).fetchall()]

    def remove_file(self, file_path: str) -> None:
        remove_file_sql = f'delete from records where file_path = "{file_path}"'

        with ContextCursor(self.__connection) as cursor:
            cursor.execute(remove_file_sql)

        self.__connection.commit()

    def __del__(self):
        self.__connection.close()
