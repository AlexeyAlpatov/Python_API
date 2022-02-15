# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json
from pprint import pprint

url = 'https://api.github.com'
user = 'AlexeyAlpatov'

response = requests.get(f'{url}/users/{user}/repos')
# pprint(response.json())

with open('repos_list.json', 'w') as file:
    json.dump(response.json(), file)

n = 1
for repos in response.json():
    print(f'{n}: Name - {repos["name"]}, url - {repos["html_url"]}')
    n += 1

# Console out
# 1: Name - python, url - https://github.com/AlexeyAlpatov/python
# 2: Name - Python_API, url - https://github.com/AlexeyAlpatov/Python_API
