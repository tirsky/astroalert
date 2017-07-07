import hashlib
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class SolarQIndex:
    # Класс для получения данных из http://www.irf.se/Observatory/?link[Magnetometers]=Data/
    # о Q-индексе
    def __init__(self, url):
        self.url = url
        self._get_html_text()
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.new_flare = None

    def _get_html_text(self):
        r = requests.get(self.url)
        self.html = r.text

    def _crawle(self):
        for li in self.soup.findAll('li'):
            if 'Preliminary real time Q index last 15 minutes' in li.text:
                self.result_text = li.text

    def _get_data(self):
        self._crawle()
        r = self.result_text.replace('Preliminary real time Q index last 15 minutes ', '')
        r = r.replace('(http://www.irf.se/maggraphs/preliminary_real_time_k_index_15_minutes)', '')
        r = r.replace('[', '')
        self.q_index = r.split(']:')
        self.q_index[0] = self.q_index[0].split('-')[1]
        self.q_index[1] = int(float(self.q_index[1].strip()))

    def get_result_hash(self):
        # Возвращает хеш результата, если хеш вернулся отличный, от того, что в базе,
        # запрашиваем результат и сохраняем его новый хеш в базу
        self._get_data()
        m = hashlib.md5()
        data = ''
        for x in self.q_index:
            data += str(x)
        m.update(data.encode())
        return m.hexdigest()

    def _ut_to_datetime(self, ut):
        dt = datetime.strptime(ut, '%d-%m-%Y %H:%M:%S')
        return dt

    def get_result(self):
        # возвращает в виде dict {datetime(): q_index} результат по Q-индекс за последние 15 минут
        self._get_data()
        new_result_dict = {}
        elem1, elem2 = self.q_index
        date = datetime.strftime(datetime.today(), '%d-%m-%Y')
        hour = self._ut_to_datetime(date + ' ' + elem1)
        new_result_dict[hour] = elem2
        return new_result_dict


s = SolarQIndex('http://www.irf.se/Observatory/?link[Magnetometers]=Data/')
print(s.get_result_hash(), s.get_result())
# 07abd4a71966e061d006972c2d5911aa {datetime.datetime(2017, 7, 7, 14, 54, 55): 0}
