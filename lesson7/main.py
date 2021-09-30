# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from time import sleep
from sys import exit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient


WEBDRIVER_PATH = 'E:\Projects\Python\selenium\chromedriver.exe'
MAIL_URL = "https://mail.ru"
MAILBOX_URL = "https://e.mail.ru/inbox/?back=1"
MAIL_LOGIN = "study.ai_172"
MAIL_PASSWD = "NextPassword172???"
MONGO_HOST = "192.168.30.92"
MONGO_PORT = 27017


debug = False


def parse_mail(mail_hdr_item):
    """Извлекает информацию о письме и возвращает её в виде словаря"""

    mail = {}
    mail['href'] = mail_hdr_item.get_attribute('href')

    # Здесь были проблемы, потому через try-catch
    try:
        item_corr = mail_hdr_item.find_element_by_xpath('.//div [@class="llc__item llc__item_correspondent"]')
    except Exception as e:
        print(e)
        return None

    mail['from'] = item_corr.find_element_by_xpath('.//*').get_attribute('title')
    mail['sender_title'] = item_corr.find_element_by_xpath('.//*').text
    mail['date'] = mail_hdr_item.find_element_by_xpath('.//div [@class="llc__item llc__item_date"]').get_attribute('title')
    mail['subject'] = mail_hdr_item.find_element_by_xpath(
        './/div [@class="llc__item llc__item_title"]/span [@class="llc__subject"]/span[1]').text
    mail['snippet'] = mail_hdr_item.find_element_by_xpath(
        './/div [@class="llc__item llc__item_title"]/span [@class="llc__snippet"]/span [@class="ll-sp__normal"]').text

    # Только для отладки
    if debug:
        print("Date: ", mail['date'],
              "\nTitle: ", mail['sender_title'],
              "\nFrom: ", mail['from'],
              "\nSubject: ", mail['subject'],
              "\nsnippet: ", mail['snippet'],
              "\nlink:", mail['href'], "\n")

    return mail


def insert_one(collection, mail_item):
    """Записывает элемент в mongodb базу mail.incoming"""

    try:
        collection.insert_one(mail_item)
    except Exception as e:
        return False
    return True


def connect_to_db(host, port):
    """Устанавливает соединение с бд mongpodb и возвращает коллекцию"""

    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client['mail']
    return db['incoming']

def main():
    """Логинится в ящик study.ai_172@mail.ru
       и созраняет информацию о входящих в БД
    """

    failed = 0
    written = 0

    try:
        collection = connect_to_db(MONGO_HOST, MONGO_PORT)
    except Exception as e:
        print("Не удалось установить соедининение с БД. Завершение программы")
        exit(-1)

    driver = webdriver.Chrome(WEBDRIVER_PATH)
    driver.get(MAIL_URL)
    input_login = driver.find_element_by_name("login")
    input_login.send_keys(MAIL_LOGIN)
    button_passwd = driver.find_element_by_xpath("//button [@class='button svelte-1tib0qz'][@data-testid='enter-password']")
    button_passwd.send_keys(Keys.ENTER)
    print(button_passwd)

    # Тормозим для надёжности
    sleep(3)

    #
    input_passwd = driver.find_element_by_xpath("//input [@class='password-input svelte-1tib0qz'] [@type='password']")
    input_passwd.send_keys(MAIL_PASSWD)
    button_login_to_mail = driver.find_element_by_xpath("//button [@class='second-button svelte-1tib0qz'][@data-testid='login-to-mail']")
    button_login_to_mail.send_keys(Keys.ENTER)

    # Тормозим для надёжности
    sleep(3)

    # Проверяем, успешно ли вошли
    current_url = driver.current_url
    if(current_url[:31] != MAILBOX_URL):
        print("Не удалось войти в ящик. Завершение программы.")
        exit(-1)

    # проверял выделение всех сообщений
    # button_select_all = driver.find_element_by_xpath('//span [@class="button2 button2_has-ico button2_has-ico-s button2_select-all button2_pure button2_only-explanation button2_short button2_ico-text-top button2_hover-support js-shortcut"]')
    # button_select_all.click()
    # sleep(1)

    mail_ref_lst = driver.find_elements_by_xpath('//a [@class="llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal"]')
    # mail_ref_lst = driver.find_elements_by_xpath('//a [@class="llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal llc_active"]')
    if(len(mail_ref_lst) == 0):
        print("Каталог входящих писем пуст. Завершение программы.")
        exit(0)

    for item in mail_ref_lst:
        mail_dict = parse_mail(item)
        if not insert_one(collection, mail_dict):
            failed += 1
            print("При записи данных в БД, произошла ошибка.")
        else:
            written += 1
            if debug:
                print(f"Элемент {item} добавлен в бд")

    sleep(5)
    driver.close()
    print(f"\nВсего записано: {written}. Всего ошибок при записи: {failed}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
