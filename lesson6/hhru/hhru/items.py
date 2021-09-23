# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re


def has_numbers(input_string):
    return bool(re.search(r'\d', input_string))

def parse_salary_min(salary):
    """парсит строку с предложением об оплате
       и возвращает строки salary_min
    """

    # Приводим строку к единому регистру
    salary = salary[0].replace("&nbsp", "").lower().strip()
    dash_ascii = salary.find("—")
    dash_utf = salary.find("–")
    from_pos = salary.find("от")
    to_pos = salary.find("до")
    salary_min = ""

    # Парсим предложение по окладу
    # если строка не содержит чисел, то выход
    if not has_numbers(salary):
        return ""

    if from_pos > -1 and to_pos > -1:
        salary_min += "".join([x if x.isdigit() else "" for x in salary[:to_pos]])
        return salary_min
        
    if from_pos == -1 and to_pos > -1:
        return ""
        
    if from_pos > -1 and to_pos == -1:
        salary_min += "".join([x if x.isdigit() else "" for x in salary[:]])
        return salary_min

    if (dash_ascii == -1) and (dash_utf == -1) :
        return ""
    else:
        index = (dash_utf if dash_ascii == -1 else dash_ascii)
        salary_min = "".join([x if x.isdigit() else '' for x in salary[: (index - 1)]])

    return salary_min

def parse_salary_max(salary):
    """парсит строку с предложением об оплате
       и возвращает строки salary_max
    """

    # Приводим строку к единому регистру
    salary = salary[0].replace("&nbsp", "").lower().strip()
    dash_ascii = salary.find("—")
    dash_utf = salary.find("–")
    from_pos = salary.find("от")
    to_pos = salary.find("до")
    salary_max = ""

    # Парсим предложение по окладу
    # если строка не содержит чисел, то выход
    if not has_numbers(salary):
        return ""

    if from_pos > -1 and to_pos > -1:
        salary_max += "".join([x if x.isdigit() else "" for x in salary[to_pos:]])
        return salary_max
        
    if from_pos == -1 and to_pos > -1:
        salary_max += "".join([x if x.isdigit() else "" for x in salary[to_pos:]])
        return salary_max
        
    if from_pos > -1 and to_pos == -1:
        return ""
        
    if (dash_ascii == -1) and (dash_utf == -1) :
        return ""
    else:
        index = (dash_utf if dash_ascii == -1 else dash_ascii)
        salary_max = "".join([x if x.isdigit() else '' for x in salary[(index + 1):]])

    return salary_max


class HhruItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field(a)

    _id = scrapy.Field()
    src = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    salary_min = scrapy.Field(output_processor=parse_salary_min)
    salary_max = scrapy.Field(output_processor=parse_salary_max)

class SjruItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field(a)

    _id = scrapy.Field()
    src = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    salary_min = scrapy.Field(output_processor=parse_salary_min)
    salary_max = scrapy.Field(output_processor=parse_salary_max)
