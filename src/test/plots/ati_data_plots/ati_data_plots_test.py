# Copyright (c) 2020 Anastasiia Birillo, Elena Lyulina

import os

import pytest

from src.test.plots.util import TO_OPEN_PLOTS
from src.main.util.consts import TEST_DATA_PATH
from src.test.test_config import to_skip, TEST_LEVEL
from src.main.plots.ati_data_plots import create_ati_data_plot

DATA = os.path.join(TEST_DATA_PATH, 'plots/data.csv')


# Just to check no errors are raised during plot creation
@pytest.mark.skipif(to_skip(current_module_level=TEST_LEVEL.PLOTS), reason=TEST_LEVEL.PLOTS.value)
class TestAtiDataPlots:

    def test_plot_creation(self) -> None:
        create_ati_data_plot(DATA, to_show=TO_OPEN_PLOTS)
