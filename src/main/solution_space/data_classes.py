# Copyright (c) 2020 Anastasiia Birillo, Elena Lyulina

import os
import ast
import logging
from datetime import datetime
from typing import List, Union, Optional

from src.main.util import consts
from src.main.util.file_util import create_file
from src.main.util.log_util import log_and_raise_error
from src.main.util.language_util import get_extension_by_language
from src.main.canonicalization.canonicalization import get_code_from_tree
from src.main.util.consts import EXPERIENCE, DEFAULT_VALUE, ACTIVITY_TRACKER_EVENTS

log = logging.getLogger(consts.LOGGER_NAME)


class AtiItem:
    def __init__(self, timestamp: datetime = DEFAULT_VALUE.DATE.value,
                 event_type: Union[ACTIVITY_TRACKER_EVENTS, DEFAULT_VALUE] = DEFAULT_VALUE.EVENT_TYPE,
                 event_data: str = DEFAULT_VALUE.EVENT_DATA.value):
        self._timestamp = timestamp
        self._event_type = event_type
        self._event_data = event_data

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def event_type(self) -> Union[ACTIVITY_TRACKER_EVENTS, DEFAULT_VALUE]:
        return self._event_type

    @property
    def event_data(self) -> str:
        return self._event_data

    # Todo: add tests
    def is_empty(self) -> bool:
        return DEFAULT_VALUE.DATE.is_equal(self._timestamp) and DEFAULT_VALUE.EVENT_DATA.is_equal(
            self._event_type.value) \
               and DEFAULT_VALUE.EVENT_DATA.is_equal(self._event_data)

    def __str__(self) -> str:
        return f'Timestamp: {self._timestamp}, event_type: {self._event_type}, event_data: {self._event_data}'

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, AtiItem):
            return False
        return self._timestamp == o._timestamp and \
               self._event_type == o._event_type and \
               self._event_data == o._event_data


class Profile:
    def __init__(self, age: int = consts.DEFAULT_VALUE.AGE.value,
                 experience: Union[EXPERIENCE, DEFAULT_VALUE] = DEFAULT_VALUE.EXPERIENCE):
        self._age = age
        self._experience = experience

    @property
    def age(self) -> int:
        return self._age

    @property
    def experience(self) -> Union[EXPERIENCE, DEFAULT_VALUE]:
        return self._experience

    def __str__(self) -> str:
        return f'Experience: {self._experience}, age: {self._age}'


class User:
    _last_id = 0

    def __init__(self, profile: Profile = None):
        self._profile = profile
        self._id = self._last_id
        self.__class__._last_id += 1

    @property
    def profile(self) -> Profile:
        return self._profile

    @property
    def id(self) -> int:
        return self._id

    def __str__(self) -> str:
        return f'Id: {self._id}, profile: {self._profile}'


class CodeInfo:
    def __init__(self, user: User, anon_tree: Optional[ast.AST] = None, timestamp: int = 0,
                 date: datetime = DEFAULT_VALUE.DATE.value, ati_actions: Optional[List[AtiItem]] = None,
                 codetracker_filename: str = None):
        self._user = user
        self._anon_tree = anon_tree
        self._ati_actions = ati_actions if ati_actions else []
        self._timestamp = timestamp
        self._date = date
        self._codetracker_filename = codetracker_filename

    @property
    def user(self) -> User:
        return self._user

    @property
    def anon_tree(self) -> ast.AST:
        return self._anon_tree

    @property
    def ati_actions(self) -> List[AtiItem]:
        return self._ati_actions

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def date(self) -> timestamp:
        return self._date

    @property
    def codetracker_filename(self):
        return self._codetracker_filename

    def __str__(self) -> str:
        return f'User: {self._user}, anon_tree: {get_code_from_tree(self._anon_tree)}, timestamp: {self._timestamp},' \
               f' date: {self._date}. Length of ati actions is {len(self._ati_actions)}'


# Todo: rename because it's about a canon tree, but it's called 'Code'?
class Code:
    _last_id = 0

    def __init__(self, canon_tree: ast.AST = None, rate: float = 0.0, file_with_code: Optional[str] = None):
        self._canon_tree = canon_tree
        self._file_with_code = file_with_code
        self._rate = rate

        self._id = self._last_id
        self.__class__._last_id += 1

    @property
    def canon_tree(self) -> ast.AST:
        return self._canon_tree

    @property
    def rate(self) -> float:
        return self._rate

    @property
    def file_with_code(self) -> Optional[str]:
        return self._file_with_code

    @file_with_code.setter
    def file_with_code(self, file_with_code: str) -> None:
        self._file_with_code = file_with_code

    def create_file_with_code(self, folder_to_write: str, name_prefix: str,
                              language: consts.LANGUAGE = consts.LANGUAGE.PYTHON) -> None:
        if not self._canon_tree:
            log_and_raise_error(f'Canon tree in the code {self} is None', log)

        extension = get_extension_by_language(language)
        file_path = os.path.join(folder_to_write, name_prefix + str(self._id) + str(extension.value))
        code = get_code_from_tree(self._canon_tree)
        create_file(code, file_path)
        self._file_with_code = file_path

    def __str__(self) -> str:
        return f'Id: {self._id}, rate: {self._rate}\nCode:\n{get_code_from_tree(self._canon_tree)}\n'

    def is_full(self) -> bool:
        return self._rate == consts.TEST_RESULT.FULL_SOLUTION.value
