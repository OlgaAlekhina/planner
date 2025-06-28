def pytest_addoption(parser):
    """ Добавляет параметр env в команду pytest """
    parser.addoption(
        '--env',
        action='store',
        default='dev',
        help='You can pass "--env prod" in pytest command for testing app in production'
    )



