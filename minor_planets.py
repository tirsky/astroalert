import hashlib
from datetime import datetime

import requests
from bs4 import BeautifulSoup

URL = 'https://ssd-api.jpl.nasa.gov/scout.api'
VMAG_LIMIT = 15


class MinorPlanet:
    # Класс для получения данных из https://ssd-api.jpl.nasa.gov/scout.api?www=1
    # о малых телах Солнечной Системы с яркостью выше 15-й зв. величины
    def __init__(self, url):
        self.url = url
        self._get_json()
        self.new_flare = None

    def _get_json(self):
        r = requests.get(self.url)
        self.json_data = r.json()

    def _get_data(self):
        vmag_limit_data = []
        sorted_list = sorted(self.json_data['data'], key=lambda d: self._ut_to_datetime(d['lastRun']), reverse=True)
        for i in sorted_list:
            if float(i['Vmag']) <= VMAG_LIMIT:
                vmag_limit_data.append(i)
        self.data = vmag_limit_data

    def get_result_hash(self):
        # Возвращает хеш результата, если хеш вернулся отличный, от того, что в базе,
        # запрашиваем результат и сохраняем его новый хеш в базу
        self._get_data()
        m = hashlib.md5()
        md5_strings = ''
        for i in self.data:
            md5_strings += str(i['lastRun'] + i['objectName'] + i['Vmag'])
        m.update(md5_strings.encode())
        return m.hexdigest()

    def _ut_to_datetime(self, ut):
        dt = datetime.strptime(ut, '%Y-%m-%d %H:%M')
        return dt

    def get_result(self):
        # возвращает в виде list of dicts результат по самому свежему объекту.
        self._get_data()
        new_result_array = []
        for i in self.data:
            new_result_dict = {}
            new_result_dict['lastRun'] = self._ut_to_datetime(i['lastRun'])
            new_result_dict['objectName'] = i['objectName']
            new_result_dict['Vmag'] = float(i['Vmag'])
            new_result_array.append(new_result_dict)
        return new_result_array


s = MinorPlanet(URL)
print(s.get_result_hash(), s.get_result())
# d41d8cd98f00b204e9800998ecf8427e []
