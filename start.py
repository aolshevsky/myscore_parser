from myscore_parser import templates
from myscore_parser.parsers import player_info, match_info, tournament_info
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep


def connect():
    driver = webdriver.Chrome("F:\ASP.NET\Test\\chromedriver")
    sleep(1)
    return driver


def load_data_by_url(url, driver):
    driver.get(url)
    return driver.page_source


def get_soup_page_by_url(url, driver):
    return BeautifulSoup(load_data_by_url(url, driver), "html.parser")


def main():
    driver = connect()
    match_url = 'https://www.myscore.com.ua/match/EezaGZxc/#match-summary'
    # match_soup = get_soup_page_by_url(match_url, driver)

    tournament_url = 'https://www.myscore.com.ua/football/england/premier-league/results/'
    tournament_soup = get_soup_page_by_url(tournament_url, driver)
    element = driver.find_element_by_xpath("//table[@class='link-more-games']/tbody/tr/td/a")

    while True:
        try:
            element.click()
            sleep(2)
        except:
            break

    tournament_soup = BeautifulSoup(driver.page_source, "html.parser")

    tournament_info.get_tournament_matches(tournament_soup)

    # match_data = match_soup.find('div', templates.periods_block)
    #
    # referee_full_name = match_info.get_referee_info(match_soup)
    # print("Судья: {referee[1]} {referee[0]}".format(referee=referee_full_name))
    #
    # for t in match_data.find_all('div', templates.periods_headers):
    #     print("Тайм: " + t.text)
    #
    # for ev in match_data.find_all('div', templates.period_row):
    #     player_ids = []
    #
    #     print("Время: {time} мин".format(time=match_info.parse_match_time(ev.find('div', templates.period_row_time).text)))
    #
    #     soccer_ball = ev.find('div', templates.period_row_soccer_ball)
    #     y_card = ev.find('div', templates.period_row_y_card)
    #     r_card = ev.find('div', templates.period_row_r_card)
    #     sub_incident = ev.find('span', templates.period_row_sub_incident_name)
    #     player_ids += match_info.get_substitution_name(ev)
    #     player_ids += match_info.get_participant_name(ev)
    #
    #     for p_url in match_info.convert_player_ids_to_url(player_ids):
    #         player_info_page = get_soup_page_by_url(p_url, driver)
    #         player_info.get_player_info(player_info_page)
    #         print(player_info.get_player_transfers(player_info_page))
    #
    #     if y_card:
    #         print("Желтая карточка")
    #     if r_card:
    #         print("Красная карточка")
    #     if soccer_ball:
    #         print("Гооол!")
    #     if sub_incident:
    #         incident = sub_incident.get_text()[1:-1]
    #         print("Инцидент: {incident}".format(incident=incident))
    #     print()

    driver.quit()


if __name__ == '__main__':
    main()
