from myscore_parser import templates
from myscore_parser.parsers import tournament_info
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep


class Bot:
    def __init__(self, url: str):
        self.driver = webdriver.Chrome("chromedriver")
        self.url = url
        self.navigate()
        self.window_handle = self.driver.window_handles[-1]

    def navigate(self):
        self.driver.get(self.url)

    def get_page_soup(self):
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def get_page_source_by_new_url(self, url: str) -> BeautifulSoup:
        prev_url, self.url = self.url, url
        self.navigate()
        return self.get_page_soup()


def main():
    tournament_url = 'https://www.myscore.com.ua/football/england/premier-league/results/'
    bot = Bot(tournament_url)

    element = bot.driver.find_element_by_xpath(templates.tournament_info_get_more_matches)

    while True:
        try:
            element.click()
            sleep(2)
        except Exception as e:
            print(e)
            break

    tournament_soup = bot.get_page_soup()

    print(*tournament_info.get_tournament_matches(bot, tournament_soup, 1), sep='\n')

    bot.driver.quit()


if __name__ == '__main__':
    main()
