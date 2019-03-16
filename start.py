from myscore_parser import templates
from myscore_parser.parsers import player_info
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
from time import sleep
import re


def connect():
    driver = webdriver.Chrome("F:\ASP.NET\Test\\chromedriver")
    sleep(1)
    return driver


def load_data_by_url(url, driver):
    driver.get(url)
    return driver.page_source


def parse_match_time(time):
    time = time[:-1]
    if re.match('\d{2,3}\+\d', time):
        add_time = time.split('+')
        return int(add_time[0]) + int(add_time[1])
    return int(time)


def get_substitution_name(element):
    substitution = element.find_all('span', templates.period_row_substitution_name)
    player_ids = []
    for sub in substitution:
        if sub['class'][0] == 'substitution-out-name':
            print("Игрок: {player} ушел с поля".format(player=sub.get_text()))
        else:
            print("Игрок: {player} вышел на поле".format(player=sub.get_text()))
        player_ids += get_participant_id(sub)

    return player_ids


def get_participant_name(element):
    player_name = element.find('span', templates.period_row_participant_name)
    if player_name:
        return get_participant_id(player_name)

    return []


def get_participant_id(soup):
    player_id_regex = re.compile('/[\S]*/')
    return player_id_regex.findall(soup.find('a')['onclick'])


def convert_player_ids_to_url(player_ids):
    result_list = []

    for player_id in player_ids:

        url = '{}{}'.format(
            templates.BASE_URL,
            player_id
        )

        result_list.append(url)

    return result_list


def get_player_info_page(url, driver):
    return BeautifulSoup(load_data_by_url(url, driver), "html.parser")


def main():
    driver = connect()
    url = 'https://www.myscore.com.ua/match/27JsGrvC/#match-summary'
    match_soup = BeautifulSoup(load_data_by_url(url, driver), "html.parser")

    # try:
    #     element = driver.find_element_by_xpath("//span[@class='participant-name']")
    #     element.click()
    #     sleep(5)
    # except Exception as e:
    #     print(e)
    #     driver.quit()

    match_data = match_soup.find('div', templates.periods_block)
    for t in match_data.find_all('div', templates.periods_headers):
        print("Тайм: " + t.text)

    for ev in match_data.find_all('div', templates.period_row):
        # print("OP:", ev.text)
        player_ids = []

        print("Время: {time} мин".format(time=parse_match_time(ev.find('div', templates.period_row_time).text)))

        soccer_ball = ev.find('div', templates.period_row_soccer_ball)
        y_card = ev.find('div', templates.period_row_y_card)
        sub_incident = ev.find('span', templates.period_row_sub_incident_name)
        player_ids += get_substitution_name(ev)
        player_ids += get_participant_name(ev)

        # print(convert_player_ids_to_url(player_ids))
        for p_url in convert_player_ids_to_url(player_ids):
            player_info_page = get_player_info_page(p_url, driver)
            player_info.get_player_info(player_info_page)
            print(player_info.get_player_transfers(player_info_page))

        if y_card:
            print("Желтая карточка")
        if soccer_ball:
            print("Гооол!")
        if sub_incident:
            incident = sub_incident.get_text()[1:-1]
            print("Инцидент: {incident}".format(incident=incident))
        print()

    driver.quit()


if __name__ == '__main__':
    main()
