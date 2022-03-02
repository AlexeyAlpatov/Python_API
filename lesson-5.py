# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о
# письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#
from pprint import pprint
import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from pymongo import MongoClient
from settings import LOGIN, PWD


def authorization():
    find_and_click(By.XPATH, '//input[@name="username"]', LOGIN).submit()
    find_and_click(By.XPATH, '//input[@name="password"]', PWD).submit()


def find_and_click(by, selector: str, text: str):
    element = wait.until(Ec.element_to_be_clickable((by, selector)))
    element.send_keys(text)
    return element


def get_url_email(element, set_url=None):
    if set_url is None:
        set_url = set()
    wait.until(Ec.presence_of_element_located((By.XPATH, element)))
    elements = driver.find_elements(By.XPATH, element)
    sub_list = [el.get_attribute('href') for el in elements]

    if sub_list[-1] in set_url:
        return set_url
    else:
        set_url.update(sub_list)
        elements[-1].send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        return get_url_email(element, set_url)


def get_data_from_email(db):
    data_list = []
    for url in tqdm(db):
        driver.get(url)
        WebDriverWait(driver, 30).until(Ec.presence_of_element_located((By.XPATH, '//h2[@class]')))
        dict_data_emails = {
            'Ссылка': url,
            'Отправитель': driver.find_element(By.XPATH, '//span[@class="letter-contact"]').get_attribute('title'),
            'Дата письма': driver.find_element(By.XPATH, '//div[@class="letter__date"]').text,
            'Заголовок письма': driver.find_element(By.XPATH, '//h2[@class]').text,
            'Тело письма': driver.find_element(By.XPATH, '//div[contains(@class, "body-content")]').text
        }
        data_list.append(dict_data_emails)
        time.sleep(1)
    return data_list


if __name__ == '__main__':
    URL = 'https://account.mail.ru/'
    options = Options()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
    s = Service('./chromedriver')
    driver = webdriver.Chrome(service=s, options=options)
    wait = WebDriverWait(driver, 30)

    client = MongoClient('localhost', 27017)
    db = client['Mail']
    mails = db.mails

    try:
        driver.get(URL)
        authorization()
        data_url = get_url_email('//a[contains(@class, "js-letter-list-item")]')
        data = get_data_from_email(data_url)
        for elem in data:
            mails.insert_one(elem)
    except Exception as Ex:
        print(Ex)
    finally:
        driver.close()
        driver.quit()
