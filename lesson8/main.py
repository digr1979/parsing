# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from os.path import abspath
from urllib import request
from time import sleep
from sys import exit

from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.keys import Keys


WEBDRIVER_PATH = 'C:\Projects\Python\parsing7\chromedriver.exe'
WEB_URL = "https://data.gov.ru/opendata"
REQUIRED_DATA = "Сведения, содержащиеся в реестре нотариусов и лиц, сдавших квалификационный экзамен"
FILE_NAME = "dataset-registry.csv"

delay = 5
debug = False


def get_open_data(url, driver_path):
    """Загружает с внешнего ресурса файл csv в кодировке UTF-8
       и возвращает полное наименование файла в файловой системе
    """

    driver = webdriver.Chrome(driver_path)
    driver.get(url)

    input_item = driver.find_element_by_xpath("//input [@placeholder='Поиск по ключевым словам...']")
    sleep(delay)

    input_item.send_keys(REQUIRED_DATA)
    sleep(delay)

    input_submit = driver.find_element_by_xpath("//input [@type='submit'] [@id='edit-submit-datasets-search']")
    input_submit.click()
    sleep(delay)

    try:
        registry_item = driver.find_element_by_xpath("//div [@typeof='sioc:Item foaf:Document dcat:Dataset']//*[@href]")
    except Exception as e:
        driver.close()
        print('Искомые данные отсутсвуют. Завершение работы.')
        exit(-1)
    registry_item.click()
    sleep(delay)

    csv_url = driver.find_element_by_xpath("//a /em [@class='placeholder'][contains(string(), 'UTF-8')]/parent::a").get_attribute('href')
    sleep(delay)

    if csv_url is None:
        driver.close()
        print('Не удалось получить данные. Завершение работы.')
        exit(-1)

    try:
        with request.urlopen(csv_url) as response, open(FILE_NAME, 'wb') as out_file:
            data = response.read() # a `bytes` object
            out_file.write(data)
    except Exception as e:
        driver.close()
        print("Ошибка при скачивании данных. Завершение работы.", e)
        exit(-1)

    driver.close()
    if debug:
        print(f"Файл {FILE_NAME} успешно скачан.")

    return abspath(FILE_NAME)


def main():
    """Загружает с внешнего ресурса файл csv в кодировке UTF-8
       и считывает его в pandas.core.frame.DataFrame
    """

    data_file = get_open_data(WEB_URL, WEBDRIVER_PATH)

    if debug:
        print(f"File is: {data_file}")

    df = pd.read_csv(data_file, sep=';', on_bad_lines='warn')
    print(df.info())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/