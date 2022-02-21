# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять
# только новые вакансии/продукты в вашу базу.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты).

import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup
from pymongo import MongoClient

# работа с БД
c_host = 'localhost'
c_port = 27017

client = MongoClient(c_host, c_port)
db = client['vac_db']
hh_col = db.hh_col


# проверка на наличии вакансии в бд
def check_vacancy(vacancy_url_db):
    try:
        vacancy_db = list(db.hh_col.find({'URL': vacancy_url_db}))
        if vacancy_db:
            res = 'Found'
        else:
            res = 'Not Found'
    except Exception:
        res = 'Not Found'
    return res


# добавление новой вакансии в бд
def insert_vacancy(vac_dict: dict):
    try:
        db.hh_col.insert_one(vac_dict)
        res = 'Success'
    except Exception:
        res = 'Error'
    return res


# поиск вакансии по зарплате
def find_vacancy(salary):
    res = list(db.hh_col.find({'$or': [{'Compensation min': {'$gte': salary}}, {'Compensation max': {'$gte': salary}}]}))
    if len(res) == 0:
        res = 'Not Found'
    return res


# сбор информации по вакансиям
position = input('Введите должность: ')
pages = int(input('Введите количество страниц: '))

base_url = 'https://novosibirsk.hh.ru'
search_url = base_url + '/search/vacancy'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/98.0.4758.82 Safari/537.36'}
vacancy_list = []

for page in range(pages):
    page_number = page + 1
    params = {
        'clusters': 'true',
        'area': '4',
        'ored_clusters': 'true',
        'enable_snippets': 'true',
        'text': position,
        'from': 'suggest_post',
        'page': page_number
    }
    response = requests.get(search_url, headers=headers, params=params)

    if response.ok:
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancy_data = dom.find_all('div', {'class': 'vacancy-serp-item'})

        for vacancy in vacancy_data:
            vacancy_dict = {}
            vacancy_info = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            vacancy_name = vacancy_info.text
            vacancy_url = vacancy_info['href']
            vacancy_url = vacancy_url.split('?')[0]
            vacancy_compensation_info = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

            if vacancy_compensation_info is None:
                vacancy_compensation = None
            else:
                vacancy_compensation = str(vacancy_compensation_info.text.replace('\u202f', ''))
                if len(vacancy_compensation) == 0:
                    vacancy_compensation = None
            try:
                min_comp = None
                max_comp = None
                currency = None
                if vacancy_compensation is not None:
                    compensation_list = vacancy_compensation.partition(' ')
                    if compensation_list[0] == 'от':
                        min_comp = int(compensation_list[2].split()[0])
                        currency = compensation_list[2].split()[1]
                    elif compensation_list[0] == 'до':
                        max_comp = int(compensation_list[2].split()[0])
                        currency = compensation_list[2].split()[1]
                    else:
                        min_comp = int(compensation_list[0])
                        max_comp = int(compensation_list[2].replace('– ', '').split()[0])
                        currency = compensation_list[2].replace('– ', '').split()[1]
            except Exception:
                min_comp = None
                max_comp = None
                currency = None

            vacancy_dict['Position'] = vacancy_name
            vacancy_dict['URL'] = vacancy_url
            vacancy_dict['Compensation min'] = min_comp
            vacancy_dict['Compensation max'] = max_comp
            vacancy_dict['Compensation currency'] = currency
            # проверяем наличие вакансии в бд и добавляем новые
            if check_vacancy(vacancy_url) == 'Not Found':
                insert_vacancy(vacancy_dict)
                print(f'Вакансия {vacancy_name} добавлена в базу')
            else:
                print(f'Вакансия {vacancy_name} уже есть в базе')

salary = int(input('Введите желаемую зарплату: '))
pprint(find_vacancy(salary))
