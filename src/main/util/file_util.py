# Copyright (c) 2020 Anastasiia Birillo, Elena Lyulina

import os
import re
import pickle
import shutil
import tempfile
from typing import Callable, Any, List, Tuple

import pandas as pd

from src.main.util.strings_util import contains_any_of_substrings
from src.main.util.consts import ACTIVITY_TRACKER_FILE_NAME, FILE_SYSTEM_ITEM, ATI_DATA_FOLDER, \
    DI_DATA_FOLDER, ISO_ENCODING, LANGUAGE, UTF_ENCODING, EXTENSION

'''
To understand correctly these functions' behavior you can see examples in a corresponding test folder.
Also, the naming convention can be helpful:
    folder_name -- just name without any slashes; 
>>> EXAMPLE: folder_name for the last folder in 'path/data/folder/' is 'folder'
    file_name -- similarly to the folder_name, but may contain its extension;
>>> EXAMPLE: file_name for the file 'path/data/file.csv' can be 'file.csv' or just 'file' (see get_file_name_from_path)
    file, folder, directory -- contain the full path
    extension -- we consider, that if extension is not empty, it is with a dot, because of os.path implementation; 
If extension is passed without any dots, a dot will be added (for example, see change_extension_to)
    parent_folder -- the second folder from the end of the path, no matter is there a trailing slash or not
>>> EXAMPLE: parent_folder for both 'path/data/file' and 'path/data/file/' is 'path/data'
'''

ItemCondition = Callable[[str], bool]


def remove_slash(path: str) -> str:
    return path.rstrip('/')


def serialize_data_and_write_to_file(path: str, data: Any) -> None:
    create_directory(get_parent_folder(path))
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def deserialize_data_from_file(path: str) -> Any:
    with open(path, 'rb') as f:
        return pickle.load(f)


def add_slash(path: str) -> str:
    if not path.endswith('/'):
        path += '/'
    return path


# For getting name of the last folder or file
# For example, returns 'folder' for both 'path/data/folder' and 'path/data/folder/'
# You can find more examples in the tests
def get_name_from_path(path: str, with_extension: bool = True) -> str:
    head, tail = os.path.split(path)
    # Tail can be empty if '/' is at the end of the path
    file_name = tail or os.path.basename(head)
    if not with_extension:
        file_name = os.path.splitext(file_name)[0]
    elif get_extension_from_file(file_name) == EXTENSION.EMPTY:
        raise ValueError('Cannot get file name with extension, because the passed path does not contain it')
    return file_name


# Not empty extensions are returned with a dot, for example, '.txt'
# If file has no extensions, an empty one ('') is returned
def get_extension_from_file(file: str) -> EXTENSION:
    return EXTENSION(os.path.splitext(file)[1])


def add_dot_to_not_empty_extension(extension: EXTENSION) -> str:
    new_extension = extension.value
    if extension != EXTENSION.EMPTY and not extension.value.startswith('.'):
        new_extension = '.' + new_extension
    return new_extension


# If need_to_rename, it works only for real files because os.rename is called
def change_extension_to(file: str, new_extension: EXTENSION, need_to_rename: bool = False) -> str:
    new_extension = add_dot_to_not_empty_extension(new_extension)
    base, _ = os.path.splitext(file)
    if need_to_rename:
        os.rename(file, base + new_extension)
    return base + new_extension


def get_parent_folder(path: str, to_add_slash: bool = False) -> str:
    path = remove_slash(path)
    parent_folder = '/'.join(path.split('/')[:-1])
    if to_add_slash:
        parent_folder = add_slash(parent_folder)
    return parent_folder


def get_parent_folder_name(path: str) -> str:
    return get_name_from_path(get_parent_folder(path), False)


def get_original_file_name(hashed_file_name: str) -> str:
    return '_'.join(hashed_file_name.split('_')[:-4])


def get_original_file_name_with_extension(hashed_file_name: str, extension: EXTENSION) -> str:
    extension = add_dot_to_not_empty_extension(extension)
    return get_original_file_name(hashed_file_name) + extension


def get_content_from_file(file: str) -> str:
    with open(file, 'r', encoding=ISO_ENCODING) as f:
        return f.read().rstrip('\n')


# File should contain the full path and its extension
def create_file(content: str, file: str) -> None:
    create_directory(os.path.dirname(file))
    with open(file, 'w') as f:
        f.write(content)


def remove_file(file: str) -> None:
    if os.path.isfile(file):
        os.remove(file)


def remove_all_png_files(root: str, condition: Callable) -> None:
    files = get_all_file_system_items(root, condition)
    for file in files:
        remove_file(file)


def does_exist(path: str) -> bool:
    return os.path.exists(path)


def create_directory(directory: str) -> None:
    os.makedirs(directory, exist_ok=True)
        
        
def remove_directory(directory: str) -> None:
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)


# To get something like 'ati_239/Main_2323434_343434.csv'
def get_file_and_parent_folder_names(file: str) -> str:
    return os.path.join(get_parent_folder_name(file), get_name_from_path(file))


def all_items_condition(name: str) -> bool:
    return True


# To get all files or subdirs (depends on the last parameter) from root that match item_condition
# Can be used to get all codetracker files, all data folders, etc.
# Note that all subdirs or files already contain the full path for them
def get_all_file_system_items(root: str, item_condition: ItemCondition = all_items_condition,
                              item_type: FILE_SYSTEM_ITEM = FILE_SYSTEM_ITEM.FILE) -> List[str]:
    items = []
    for fs_tuple in os.walk(root):
        for item in fs_tuple[item_type.value]:
            if item_condition(item):
                items.append(os.path.join(fs_tuple[FILE_SYSTEM_ITEM.PATH.value], item))
    return items


def extension_file_condition(extension: EXTENSION) -> ItemCondition:
    def has_this_extension(name: str) -> bool:
        return get_extension_from_file(name) == extension
    return has_this_extension


# To get all codetracker files
def ct_file_condition(name: str) -> bool:
    return ACTIVITY_TRACKER_FILE_NAME not in name and extension_file_condition(EXTENSION.CSV)(name)


def contains_substrings_condition(substrings: List[str]) -> ItemCondition:
    def contains_these_substrings(name: str) -> bool:
        return contains_any_of_substrings(name, substrings)
    return contains_these_substrings


def match_condition(regex: str) -> ItemCondition:
    def does_name_match(name: str) -> bool:
        return re.fullmatch(regex, name) is not None
    return does_name_match


# To get all subdirs that contain ct and ati data
def data_subdirs_condition(name: str) -> bool:
    return ATI_DATA_FOLDER in name or DI_DATA_FOLDER in name


# To get path to the result folder that is near to the original folder
# and has the same name but with a suffix added at the end
def get_result_folder(folder: str, result_name_suffix: str) -> str:
    result_folder_name = get_name_from_path(folder, False) + '_' + result_name_suffix
    return os.path.join(get_parent_folder(folder), result_folder_name)


def create_folder_and_write_df_to_file(folder_to_write: str, file_to_write: str, df: pd.DataFrame) -> None:
    create_directory(folder_to_write)

    # Get error with this encoding=ENCODING on ati_225/153e12:
    # "UnicodeEncodeError: 'latin-1' codec can't encode character '\u0435' in position 36: ordinal not in range(256)"
    # So change it then to 'utf-8'
    try:
        df.to_csv(file_to_write, encoding=ISO_ENCODING, index=False)
    except UnicodeEncodeError:
        df.to_csv(file_to_write, encoding=UTF_ENCODING, index=False)


# To write a dataframe to the result_folder remaining the same file structure as it was before
# For example, for path home/codetracker/data and file home/codetracker/data/folder1/folder2/ati_566/file.csv
# the dataframe will be written to result_folder/folder1/folder2/ati_566/file.csv
def write_result(result_folder: str, path: str, file: str, df: pd.DataFrame) -> None:
    # check if file is in a path, otherwise we cannot reproduce its structure inside of result_folder
    if path != file[:len(path)]:
        raise ValueError('File is not in a path')
    path_from_result_folder_to_file = file[len(path):]
    file_to_write = os.path.join(result_folder, path_from_result_folder_to_file)
    folder_to_write = get_parent_folder(file_to_write)
    create_folder_and_write_df_to_file(folder_to_write, file_to_write, df)


# To write a dataframe to the result_folder based on the language and remaining only the parent folder structure
# For example, for file path/folder1/folder2/ati_566/file.csv and python language the dataframe will be
# written to result_folder/python/ati_566/file.csv
def write_based_on_language(result_folder: str, file: str, df: pd.DataFrame,
                            language: LANGUAGE = LANGUAGE.PYTHON.value) -> None:
    folder_to_write = os.path.join(result_folder, language.value, get_parent_folder_name(file))
    file_to_write = os.path.join(folder_to_write, get_name_from_path(file))
    create_folder_and_write_df_to_file(folder_to_write, file_to_write, df)


def pair_in_and_out_files(in_files: list, out_files: list) -> List[Tuple[str, str]]:
    pairs = []
    for in_file in in_files:
        out_file = re.sub(r'in(?=[^in]*$)', 'out', in_file)
        if out_file not in out_files:
            raise ValueError(f'List of out files does not contain a file for {in_file}')
        pairs.append((in_file, out_file))
    return pairs
