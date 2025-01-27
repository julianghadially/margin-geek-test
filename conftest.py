import pytest
def pytest_addoption(parser):
    parser.addoption("--mode", action="store", default=None)
    parser.addoption("--mini", action="store", default=None)
    parser.addoption("--location", action="store", default=None)

@pytest.fixture
def command_line_args(request):
    args = {}
    args['mode'] = request.config.getoption('--mode')
    args['mini'] = request.config.getoption('--mini')
    args['location'] = request.config.getoption('--location')
    return args