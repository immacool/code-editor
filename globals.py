import os

PROJECT_DIRECTORY = os.path.dirname(__file__).replace('\\', '/').replace('c:/', 'C:/')
SETTINGS_PATH = os.path.join(PROJECT_DIRECTORY, 'settings.json')
WINDOW_ICON = os.path.join(PROJECT_DIRECTORY, 'logo.png')
