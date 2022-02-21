from pymongo import MongoClient
from pprint import pprint

c_host = 'localhost'
c_port = 27017

client = MongoClient(c_host, c_port)
db = client['vac_db']
hh_col = db.hh_col


# проверка на наличии вакансии в бд
def check_vacancy(vacancy_url):
    try:
        vacancy = list(db.hh_col.find({'URL': vacancy_url}))
        if vacancy:
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
