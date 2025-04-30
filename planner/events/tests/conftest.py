def pytest_addoption(parser):
    parser.addoption(
        '--env',
        action='store',
        default='dev',
        help='Choose prod when test app in production'
    )



