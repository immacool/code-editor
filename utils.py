import json
from pprint import pprint
from globals import SETTINGS_PATH


class SettingsInstance:

    def __init__(self):
        with open(SETTINGS_PATH, 'r', encoding='utf8') as f:
            self.__settings = json.load(f)
        self.refresh()

    def refresh(self):
        self.hotkeys_settings = self.__settings.get('Горячие клавиши')
        self.default_theme = self.__settings.get('Тема по умолчанию')
        self.run_settings = self.__settings.get('Настройки запуска')
        self.recent_files = self.__settings.get('Последние файлы')

    def save(self):
        with open(SETTINGS_PATH, 'w', encoding='utf8') as f:
            json.dump(self.__settings, f, ensure_ascii=False)

    def set(self, key: str, value):
        self.__settings[key] = value
        self.save()

    def update(self, chains: dict):
        self.__settings.update(chains)
        self.save()
        
    def add_recent(self, file_path):
        recent: list = self.__settings['Последние файлы']
        if file_path in recent:
            return
        
        if len(recent) >= 10:
            recent.pop(0)
            
        self.__settings.update({'Последние файлы': recent + [file_path]})
        self.refresh()
        self.save()

    def describe(self):
        pprint(self.__settings)


if __name__ == '__main__':
    settings = SettingsInstance()
    settings.describe()
