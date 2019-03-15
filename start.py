from my_score import templates
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import re


def load_script_data(driver):
    error = None
    xpath = (
        '/html/body/div[3]/div[2]/div/div[2]/div[1]/div[7]/table/tbody/tr/td/a'
    )
    res = driver.find_element_by_xpath(xpath)
    while not error:
        try:
            res.click()
            sleep(1)
        except BaseException:
            error = True
            print('load script data')


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
    for sub in substitution:
        if sub['class'][0] == 'substitution-out-name':
            print("Игрок: {player} ушел с поля".format(player=sub.text))
        else:
            print("Игрок: {player} вышел на поле".format(player=sub.text))


def get_participant_name(element):
    player_name = element.find('span', templates.period_row_participant_name)
    if player_name:
        print("Игрок: {player}".format(player=player_name.text))


def main():
    driver = connect()
    url = 'https://www.myscore.com.ua/match/27JsGrvC/#match-summary'
    soup = BeautifulSoup(load_data_by_url(url, driver), "html.parser")

    match_data = soup.find('div', templates.periods_block)
    for t in match_data.find_all('div', templates.periods_headers):
        print("Тайм: " + t.text)

    for ev in match_data.find_all('div', templates.period_row):
        # print("OP:", ev.text)
        print("Время: {time} мин".format(time=parse_match_time(ev.find('div', templates.period_row_time).text)))

        soccer_ball = ev.find('div', templates.period_row_soccer_ball)
        y_card = ev.find('div', templates.period_row_y_card)
        sub_incident = ev.find('span', templates.period_row_sub_incident_name)
        get_substitution_name(ev)
        get_participant_name(ev)

        if y_card:
            print("Желтая карточка")
        if soccer_ball:
            print("Гооол!")
        if sub_incident:
            incident = sub_incident.text[1:-1]
            print("Инцидент: {incident}".format(incident=incident))
        print()

    driver.quit()


if __name__ == '__main__':
    main()
