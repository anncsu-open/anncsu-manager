# type: ignore
# flake8: noqa ANN201

__copyright__ = "Copyright 2025-2026, GeoBeyond.it"
__license__ = "GPL version 3"
__email__ = "info@geobeyond.it"
__revision__ = "$Format:%H$"

import pytest

from ..testing.utilities import TestTaskRunner
from ..tools.custom_logging import (
    LogTarget,
    get_log_level_key,
    setup_logger,
    teardown_logger,
)
from ..tools.resources import plugin_name
from ..tools.settings import set_setting


@pytest.fixture(scope="session")
def initialize_logger(qgis_iface):
    set_setting(get_log_level_key(LogTarget.FILE), "NOTSET")
    setup_logger(plugin_name(), qgis_iface)
    yield
    teardown_logger(plugin_name())


@pytest.fixture()
def task_runner(initialize_logger):
    return TestTaskRunner()
