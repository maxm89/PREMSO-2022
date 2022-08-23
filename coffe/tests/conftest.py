"""
A custom conftest file, allowing to run

    py.test --quick

which will exclude all tests marked as

    @pytest.mark.slow

copied and modified from https://docs.pytest.org/en/latest/example/simple.html
"""

import pytest


def pytest_addoption(parser):
    parser.addoption("--quick", action="store_true",
                     default=False, help="skip slow tests")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--quick"):
        # --quick given in cli: skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="does not run with --quick option")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
