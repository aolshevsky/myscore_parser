from myscore_parser import templates
from myscore_parser import start
from myscore_parser.parsers import player_info
from bs4 import BeautifulSoup
import re


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


def get_referee_info(match_soup):
    match_info = match_soup.find('div', templates.match_info)
    match_info_content = match_info.find_all('div', templates.match_info_content)
    full_name = match_info_content[0].get_text().split()
    return full_name[2], full_name[1]


def get_match_info(bot):
    # match_url = 'https://www.myscore.com.ua/match/EezaGZxc/#match-summary'
    # bot = Bot(match_url)
    try:
        match_soup = bot.get_page_source_by_new_url(bot.driver.current_url)

        print(bot.driver.current_url)
        match_data = match_soup.find('div', templates.periods_block)

        referee_full_name = get_referee_info(match_soup)
        print("Судья: {referee[1]} {referee[0]}".format(referee=referee_full_name))

        for t in match_data.find_all('div', templates.periods_headers):
            print("Тайм: " + t.text)

        for ev in match_data.find_all('div', templates.period_row):
            player_ids = []

            print("Время: {time} мин".format(time=parse_match_time(ev.find('div', templates.period_row_time).text)))

            soccer_ball = ev.find('div', templates.period_row_soccer_ball)
            y_card = ev.find('div', templates.period_row_y_card)
            r_card = ev.find('div', templates.period_row_r_card)
            sub_incident = ev.find('span', templates.period_row_sub_incident_name)
            player_ids += get_substitution_name(ev)
            player_ids += get_participant_name(ev)

            for p_url in convert_player_ids_to_url(player_ids):
                player_info_page = bot.get_page_source_by_new_url(p_url)
                player_info.get_player_info(player_info_page)
                print(player_info.get_player_transfers(player_info_page))

            if y_card:
                print("Желтая карточка")
            if r_card:
                print("Красная карточка")
            if soccer_ball:
                print("Гооол!")
            if sub_incident:
                incident = sub_incident.get_text()[1:-1]
                print("Инцидент: {incident}".format(incident=incident))
            print()

    except BaseException as e:
        print(e)

    # bot.driver.quit()


def main():
    match_url = 'https://www.myscore.com.ua/match/EezaGZxc/#match-summary'
    bot = start.Bot(match_url)
    get_match_info(bot)


if __name__ == '__main__':
    main()
