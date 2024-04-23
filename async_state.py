import multiprocessing
from typing import TypeVar

T = TypeVar('T')


class AsyncState:
    def __init__(self, value: T):
        self.__value = value
        self.__lock = multiprocessing.Lock()

    @property
    def value(self) -> T:
        with self.__lock:
            return self.__value

    @value.setter
    def value(self, value: T):
        with self.__lock:
            self.__value = value
