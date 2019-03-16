from myscore_parser import templates
from myscore_parser.parsers import player_info, match_info, tournament_info
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep


class Bot:
    def __init__(self, url):
        self.driver = webdriver.Chrome("chromedriver")
        self.url = url
        self.navigate()

    def navigate(self):
        self.driver.get(self.url)

    def get_page_source(self):
        return self.driver.page_source

    def get_page_source_by_new_url(self, url):
        prev_url, self.url = self.url, url
        self.navigate()
        return self.get_page_source()

    def quit_driver(self):
        self.driver.quit()


def load_data_by_url(url, driver):
    driver.get(url)
    return driver.page_source


def get_soup_page_by_url(url, driver):
    return BeautifulSoup(load_data_by_url(url, driver), "html.parser")


def main():
    tournament_url = 'https://www.myscore.com.ua/football/england/premier-league/results/'
    bot = Bot(tournament_url)

    element = bot.driver.find_element_by_xpath(templates.tournament_info_get_more_matches)

    while True:
        try:
            element.click()
            sleep(2)
        except:
            break

    tournament_soup = BeautifulSoup(bot.driver.page_source, "html.parser")

    print(*tournament_info.get_tournament_matches(tournament_soup), sep='\n')

    bot.quit_driver()


if __name__ == '__main__':
    main()
