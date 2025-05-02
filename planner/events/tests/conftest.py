def pytest_addoption(parser):
    """ Добавляет параметр env в команду pytest """
    parser.addoption(
        '--env',
        action='store',
        default='dev',
        help='Choose prod when test app in production'
    )



