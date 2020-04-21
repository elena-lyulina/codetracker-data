# Copyright (c) 2020 Anastasiia Birillo, Elena Lyulina

import os
import sys
import logging

import pandas as pd

from src.main.util import consts
from src.main.util.file_util import add_slash
from src.main.util.consts import PATH_CMD_ARG, TASK
from src.main.solution_space.hint import HintGetter
from src.main.util.log_util import configure_logger
from src.main.solution_space.data_classes import User
from src.main.preprocessing.preprocessing import preprocess_data
from src.main.splitting.splitting import split_tasks_into_separate_files
from src.main.solution_space.solution_space_handler import construct_solution_graph
from src.main.solution_space.solution_space_visualizer import SolutionSpaceVisualizer

pd.set_option('display.max_rows', 250)
pd.set_option('display.max_columns', 100)

log = logging.getLogger(consts.LOGGER_NAME)


def __get_data_path() -> str:
    args = sys.argv
    path = args[args.index(PATH_CMD_ARG) + 1]
    if not os.path.isdir(path):
        log.error(f'It is not a folder, passed path is {path}')
        sys.exit(1)
    return add_slash(path)


def main() -> None:
    configure_logger()
    path = __get_data_path()

    # Preprocess data before splitting
    # preprocess_data(path)

    # Path should contain files after preprocessing with tests results
    # split_tasks_into_separate_files(path)

    source = 'a = int(input())\nb = int(input())\nn = int(input())'
    user = User()

    # graph = deserialize_data_from_file(f'/home/elena/workspaces/python/codetracker-data/data/pies_solution_graph{consts.EXTENSION.PICKLE.value}')
    # serialize_data_and_write_to_file(f'/home/elena/workspaces/python/codetracker-data/data/pies_solution_graph{consts.EXTENSION.PICKLE.value}', graph)

    graph = construct_solution_graph(path, TASK.PIES)

    gv = SolutionSpaceVisualizer(graph)
    graph_representation_path = gv.create_graph_representation(name_prefix='graph_all_space_final_version')
    print(graph_representation_path)

    hint_getter = HintGetter(graph)
    hint = hint_getter.get_hint(source, user)
    print(hint.recommended_code)


if __name__ == '__main__':
    main()
