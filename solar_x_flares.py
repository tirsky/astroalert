import hashlib
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class SolarXFlares:
    def __init__(self, url):
        self.url = url
        self._get_html_text()
        self.new_flare = None
        self.soup = BeautifulSoup(self.html, 'lxml')

    def _get_html_text(self):
        r = requests.get(self.url)
        self.html = r.text

    def _crawle(self):
        res = self.soup.find('p', {'class': 'file-text'})
        self.result_text = res.text

    def _get_data(self):
        self._crawle()
        r = self.result_text.replace('\n', '')
        stripped = [line.strip() for line in r.split(':')]
        self.new_flare = stripped[0:5]
        if self.new_flare[-1] == 'Approximate Flare Start':
            self.new_flare.pop()

    def get_result_hash(self):
        # Возарвщает хеш результата, если хеш вернулся отличный, от того, что в базе,
        # запрашиваем результат и сохраняем его новый хеш в базу
        self._get_data()
        m = hashlib.md5()
        data = ''
        for x in self.new_flare:
            data += x
        m.update(data.encode())
        return m.hexdigest()

    def _ut_to_datetime(self, ut):
        dt = datetime.strptime(ut, '%d-%m-%Y %H%M')
        return dt

    def get_result(self):
        # возвращает в виде dict {Name : datetime()} результат по вспышкам
        self._get_data()
        new_result_dict = {}
        print(self.new_flare)
        elem1, elem2, elem3, elem4 = self.new_flare
        if len(self.new_flare) == 5:
            elem5 = self.new_flare[-1]
        new_result_dict[elem1] = self._ut_to_datetime(
            elem2.replace('Approximate Flare Maximum', '').replace(' UT ', ''))
        max_date = self._ut_to_datetime(elem3.split('UT')[0].rstrip())
        end_date = self._ut_to_datetime(elem4.split('UT')[0].rstrip())
        new_result_dict.update({'Approximate Flare Maximum': max_date})
        new_result_dict.update({'Approximate Flare End': end_date})
        return new_result_dict

s = SolarXFlares('http://www.sws.bom.gov.au/Solar/1/8')
print(s.get_result_hash(), s.get_result())

# {'Approximate Flare Start': datetime.datetime(2017, 7, 3, 16, 13),
# 'Approximate Flare Maximum': datetime.datetime(2017, 7, 3, 16, 15),
# 'Approximate Flare End': datetime.datetime(2017, 7, 3, 16, 17)}
# 697ade06577c29e1ab8ca53b9c78920c
