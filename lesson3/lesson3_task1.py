############################################
#
# Author: Dmitry Gromov
# Date: 2021-09-06
# Description: homework2 task1
#
###########################################


import sys 


import requests
import pandas as pd
import lxml
import pandas as pd
from bs4 import BeautifulSoup
from transliterate import translit
from tabulate import tabulate
from pymongo import MongoClient
from zlib import adler32, crc32


# https://hh.ru/search/vacancy?area=1&fr=omSearchLine=true&st=searchVacancy&text=перограммист+1с
# https://www.superjob.ru/vakansii/programmist-1s.html?geo%5Bt%5D%5B0%5D=4

# HH_URL = "https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text="
HH_URL = "https://hh.ru/search/vacancy"
SJ_URL = "https://www.superjob.ru/vakansii/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)" \
            " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
MONGOHOST = "192.168.30.92"
MONGOPORT = 27017


debug = False


# def get_html(url, vacancy):
def get_html(url, params):
    """Возвращаем текст полученной  страницы"""

    # params = {'area': 1, 'fromSearchline': 'true', 'st': 'searchVacancy', 'text': vacancy}
    return requests.get(url, params=params, headers=HEADERS)


def parse_html_hh(html, pages_to_parse):
    """Получает дааные о вакансиях с сайта hh.ru"""

    # Возвращаемый список вакансий
    vacancy_lst = []

    soup = BeautifulSoup(html, 'lxml')

    pager_block = soup.find(name='div', attrs={"data-qa": "pager-block"})
    bloko_buttons = pager_block.find_all(name='a', class_="bloko-button", attrs={"data-qa": "pager-page"})
    total_pages = bloko_buttons[-1].text

    if int(total_pages) > int(pages_to_parse):
        total_pages = str(pages_to_parse)

    # Извлекаем ссылку на страницы результата поиска
    href = bloko_buttons[-1].attrs['href']
    index = href.rfind('=')
    href = href[0: index]

    # Обходим необходимое кол-во страниц
    for page_num in range(0, int(total_pages)):
        current_href = "https://hh.ru" + href + "=" + str(page_num)
        try:
            response = requests.get(current_href, headers=HEADERS)
        except Exception as e:
            print("При получении данных, возникла ошибка. Выход.")
            sys.exit(-1)

        if response.status_code != 200:
            print("При получении данных, возникла ошибка. Выход.")
            sys.exit(-1)

        # soup = BeautifulSoup(response.text, 'lxml')
        # Получаем фрейм с вакансиями
        frame = soup.find(class_="vacancy-serp", attrs={"data-qa": "vacancy-serp__results"})

        # Парсим вакансии
        vacancy_items = frame.find_all(class_="vacancy-serp-item")

        for item in vacancy_items:
            vacancy_src = "hh.ru"
            vacancy_info = item.find(class_="bloko-link", attrs={'data-qa': "vacancy-serp__vacancy-title"})
            vacancy_title = vacancy_info.contents[0]
            vacancy_href = vacancy_info.attrs['href']
            vacancy_crc = crc32(vacancy_href.encode("utf-8"))
            # class ="bloko-link bloko-link_secondary" data-qa="vacancy-serp__vacancy-employer" href="/employer/1605113" > АРДЕЙЛ < / a >

            # employer = item.find(name="a", class_="bloko-link bloko-link_secondary", attrs={'data-qa': "vacancy-serp__vacancy-employer"}).text
            employer = item.find(name="a", class_="bloko-link bloko-link_secondary", attrs={'data-qa': "vacancy-serp__vacancy-employer"})
            if employer is None:
                # <div class="vacancy-serp-item__meta-info-company">Международная торговая компания. На рынке более 7 лет.</div>
                employer_title = item.find(name="div", class_="vacancy-serp-item__meta-info-company").text
                employer_href = "нет данных"
            else:
                try:
                    employer_title = employer.text
                    employer_href = "https://hh.ru" + employer.attrs["href"]
                except Exception as e:
                    print(employer)

            compensation_span = item.find(name='span', attrs={'data-qa': "vacancy-serp__vacancy-compensation"})
            if compensation_span is None:
                # salary_min = salary_max = "нет данных"
                salary_min = salary_max = 0
                vacancy_lst.append([crc32(vacancy_href.encode('utf-8')), vacancy_src, vacancy_title, salary_min, salary_max, vacancy_href, employer_title, employer_href])
                continue

            salary_text = compensation_span.text
            salary_min, salary_max = parse_salary(salary_text)
            vacancy_lst.append([crc32(vacancy_href.encode('utf-8')),vacancy_src, vacancy_title, salary_min, salary_max, vacancy_href, employer_title, employer_href])

    return vacancy_lst


def parse_html_sj(html):
    """"""

    # https://www.superjob.ru/vakansii/vospitatel-detskogo-sada.html?geo%5Bt%5D%5B0%5D=4&page=2

    # Возвращаемый список вакансий
    vacancy_lst = []

    soup = BeautifulSoup(html, 'lxml')
    result_items = soup.find_all(class_="Fo44F QiY08 LvoDO")

    for item in result_items:
        title_class = item.find(class_="_1h3Zg _2rfUm _2hCDz _21a7u")
        title_subclass = title_class.find(name="a", class_="icMQ_")
        title_text_items = title_subclass.find_all(name="span", class_="_1rS-s")
        vacancy_title = ""
        for text_item in title_text_items:
            vacancy_title += text_item.text + " "
        vacancy_title.strip()

        vacancy_src = "superjob.ru"
        vacancy_title = vacancy_title
        vacancy_href = "https://www.superjob.ru" + title_subclass.attrs['href']
        vacancy_crc = crc32(vacancy_href.encode('utf-8'))

        salary_class = item.find(name="span", class_="f-test-text-company-item-salary")
        salary_class_item_lst = salary_class.contents

        salary_text = ""
        for salary_item_text in salary_class_item_lst:
            salary_text += salary_item_text.text

        # # Парсим предложение по окладу
        salary_min, salary_max = parse_salary(salary_text)

        employer_span = item.find(name="span", class_="_1h3Zg _3Fsn4 f-test-text-vacancy-item-company-name e5P5i _2hCDz _2ZsgW _2SvHc")
        if employer_span is None:
            continue

        employer_class = employer_span.find(name="a", class_="icMQ_")
        employer_title = employer_class.text
        employer_href = "https://www.superjob.ru" + employer_class.attrs['href']

        vacancy_lst.append([vacancy_crc, vacancy_src, vacancy_title, salary_min, salary_max, vacancy_href, employer_title, employer_href])

    return vacancy_lst


def parse_salary(salary_text):
    """парсит строку с предложением об оплате
       и возвращает строки salary_min и salary_max
    """

    # Приводим строку к единому регистру
    salary_text = salary_text.lower().strip()

    # Парсим предложение по окладу
    if salary_text.find("по") > -1:
        salary_min = 0
        salary_max = 0
    elif salary_text.find("от") > -1:
        salary_min = ""
        salary_min += "".join([x if x.isdigit() else "" for x in salary_text[:]])
        salary_max = 0
    elif salary_text.find("до") > -1:
        salary_min = 0
        salary_max = ""
        salary_max += "".join([x if x.isdigit() else "" for x in salary_text[:]])
    else:
        dash_ascii = salary_text.find("—")
        dash_utf = salary_text.find("–")
        if (dash_ascii == -1) and (dash_utf == -1) :
            salary_min = 0
            salary_max = ""
            salary_max += "".join([x if x.isdigit() else "" for x in salary_text[:]])
        else:
            index = (dash_utf if dash_ascii == -1 else dash_ascii)
            salary_min = salary_max = ""
            salary_min = "".join([x if x.isdigit() else '' for x in salary_text[: (index - 1)]])
            salary_max = "".join([x if x.isdigit() else '' for x in salary_text[(index + 1):]])

    return int(salary_min), int(salary_max)


def connect_mongodb(host, port):
    """подключается к серверу mongodb
       и возвращает подключение к базу 'vacancies'
    """

    client = MongoClient(host, port)
    return client['vacancies']


def update_mongodb(db, data):
    """Добавляет (обновляет данные в mongodb"""

    result = db.collection.find({'crc': data['crc']})
    if result.count() == 0:
        ret = db.collection.insert_one(data)
        if debug:
            print(f"New vacancy {data['vacancy']} with crc {data['crc']} has been added to db")
    else:
        if debug:
            for row in result:
                print(row)
            print("Data does already exist. Skipping")

    return None


def select_vacancies(db, salary_gt):
    """Возвращает результат запроса к коллекции
       содержащий документы с мимнимальным окладом >= salary_gt
    """

    return db.collection.find({'salary_min': {'$gt': salary_gt}})


def main():
    """ Возвращает следующие данные в виде pandas.DataFrame
        | crc | источник | вакансия | оклад мин | оклад мах | ссылка | организация | ссылка на организацию
    """

    vacancy_lst = []

    vacancy = ""
    while(len(vacancy) == 0):
        vacancy = str.strip(input("Укажите вакансию для поиска:"))

    pages_to_parse = ""
    while(len(pages_to_parse) == 0):
        pages_to_parse = str.strip(input("Укажите сколько страниц парсить:"))


    # # Получаем данные из hh.ru
    hh_params = {'area': 1, 'fromSearchline': 'true', 'st': 'searchVacancy', 'text': vacancy}

    try:
        ret = get_html(HH_URL, hh_params)
    except Exception as e:
        print("Ошибка при загрузке страницы: %str" %(e))
        return sys.exit(-1)

    if ret.status_code == 200:
        vacancy_lst.extend(parse_html_hh(ret.text, pages_to_parse))
    else:
        print("Сервер вернул код: %d" %(ret.status_code))
        return sys.exit(-1)

    #########################################################################################

    # Получаем данные из superjob.ru
    sj_vacancy_lst = []
    sj_params = {"keywords": vacancy}
    sj_params = None
    sj_url = "https://www.superjob.ru/vacancy/search/?keywords=" + vacancy.replace(" ", "%20") + "&geo%5Bt%5D%5B0%5D"
    sj_current_url = sj_url
    page_count = 1
    pages_to_parse = int(pages_to_parse)

    while(page_count <= pages_to_parse):
        try:
            ret = get_html(sj_current_url, sj_params)
        except Exception as e:
            print("Ошибка при загрузке страницы: %str" %(e))
            return sys.exit(-1)

        if ret.status_code == 200:
            sj_vacancy_lst.extend(parse_html_sj(ret.text))
        else:
            print("Сервер вернул код: %d" %(ret.status_code))
            return sys.exit(-1)

        page_count += 1
        sj_current_url = sj_url + "&page=" + str(page_count)

    vacancy_lst.extend(sj_vacancy_lst)

    df = pd.DataFrame(data = vacancy_lst, columns=['crc', 'source', 'vacancy', 'salary_min', 'salary_max', 'vacancy_href', 'employer', 'employer_href'])
#    if debug:
    df.info()
    print(tabulate(df, headers='keys', tablefmt='psql'))

    db = connect_mongodb(MONGOHOST, MONGOPORT)

    rows = df.to_dict(orient='records')
    for row in rows:
        if debug:
            print(row)
        try:
            update_mongodb(db, row)
        except Exception as e:
            print(e)

    salary_gt = int(input("Укажите оклад >= для отбора вакансий: "))
    try:
        result = select_vacancies(db, salary_gt)
    except Exception as e:
        print(e)

    for row in result:
        print(row)

    return None


if __name__ == '__main__':
    """
    """

    main()
