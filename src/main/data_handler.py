import pandas as pd
import numpy as np
from src.main import consts


# Todo: add logger


def __profile_column_handler(data: pd.DataFrame, column: consts.CODE_TRACKER_COLUMN,
                             default_value: consts.DEFAULT_VALUES):
    values = data[column].unique()
    index = np.argwhere((values == default_value) | pd.isnull(values))
    if (index.shape[0] == 0 and len(values) > 1) or len(values) > 2:
        # it is an invalid file
        return -1
    values = np.delete(values, index)
    if len(values) == 1:
        return values[0]
    return default_value


def get_age(data: pd.DataFrame):
    return __profile_column_handler(data, consts.CODE_TRACKER_COLUMN.AGE.value, consts.DEFAULT_VALUES.AGE.value)


def get_experience(data: pd.DataFrame):
    return __profile_column_handler(data, consts.CODE_TRACKER_COLUMN.EXPERIENCE.value,
                                    consts.DEFAULT_VALUES.EXPERIENCE.value)


def __get_extension_by_file_name(file_name: str):
    parts = file_name.split(".")
    return parts[-1]


def __get_extension_by_language(language: str):
    for extension, language in consts.LANGUAGES_DICT.items():
        if language == language:
            return extension
    return None


def __get_language_name(extension: str):
    return consts.LANGUAGES_DICT.get(extension, consts.NOT_DEFINED_LANGUAGE)


# If we have a few languages, we return NOT_DEFINED, else we return the language.
# If all files have the same extension, then we return a language, which matches to this extension (it works for all
# languages for LANGUAGES_DICT from const file)
# For example, we have a set of files: a.py, b.py. The function returns PYTHON because we have one extension for all
# files.
# For a case: a.py, b.p and c.java the function returns NOT_DEFINED because the files have different extensions
def get_language(data: pd.DataFrame):
    values = data[consts.CODE_TRACKER_COLUMN.FILE_NAME.value].unique()
    extensions = set(map(__get_extension_by_file_name, values))
    if len(extensions) == 1:
        return __get_language_name(extensions.pop())
    return consts.NOT_DEFINED_LANGUAGE


def __get_file_name_from_path(file_path: str):
    return file_path.split('/')[-1]


def __get_original_file_name(file_name: str, extension: str):
    return "_".join(file_name.split('_')[:-4]) + '.' + extension


def __remove_nan(items: list):
    return list(filter(lambda x: not pd.isnull(x), items))


def get_project_file_name(file_name: str, language: str, activity_tracker_data: pd.DataFrame):
    extension = __get_extension_by_language(language)
    file_name = __get_original_file_name(file_name, extension)
    if activity_tracker_data is not None:
        paths = __remove_nan(activity_tracker_data[consts.ACTIVITY_TRACKER_COLUMN.CURRENT_FILE.value].unique())
        file_names = list(map(__get_file_name_from_path, paths))
        if file_name not in file_names:
            raise ValueError('Activity tracker data does not contain the original file ' + file_name)

    return file_name