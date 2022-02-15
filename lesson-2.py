# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность)
# с сайтов HH. Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
# - Наименование вакансии.
# - Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# - Ссылку на саму вакансию.
# - Сайт, откуда собрана вакансия.
# Сохраните в json либо csv.

# https://novosibirsk.hh.ru/search/vacancy?clusters=true&area=4&ored_clusters=true&enable_snippets=true&salary=&text=Python&from=suggest_post
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup

position = input('Введите должность: ')
pages = int(input('Введите количество страниц: '))

base_url = 'https://novosibirsk.hh.ru'
search_url = base_url + '/search/vacancy'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
vacancy_list = []

for page in range(pages):
    page_number = page + 1
    params = {'clusters': 'true', 'area': '4', 'ored_clusters': 'true', 'enable_snippets': 'true', 'text': position, 'from': 'suggest_post', 'page': page_number}
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
            vacancy_compensation_info = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'})

            if vacancy_compensation_info is None:
                vacancy_compensation = 'None'
            else:
                vacancy_compensation = str(vacancy_compensation_info.text.replace('\u202f', ''))
                if len(vacancy_compensation) == 0:
                    vacancy_compensation = 'None'
            min_comp = 'None'
            max_comp = 'None'
            currency = 'None'

            if vacancy_compensation != 'None':
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

            vacancy_dict['Position'] = vacancy_name
            vacancy_dict['URL'] = vacancy_url
            vacancy_dict['Compensation min'] = min_comp
            vacancy_dict['Compensation max'] = max_comp
            vacancy_dict['Compensation currency'] = currency
            vacancy_list.append(vacancy_dict)

with open('vacancy.json', 'w') as file:
    json.dump(vacancy_list, file, ensure_ascii=False)
