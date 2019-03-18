from myscore_parser import templates, start
from myscore_parser.parsers import player_info, team_info, helpers
from time import sleep
import re


def parse_match_time(time: str):
    time = time[:-1]
    if re.match('\d{2,3}\+\d', time):
        add_time = time.split('+')
        return get_period_name(int(add_time[0])), int(add_time[0]) + int(add_time[1])
    return get_period_name(int(time)), int(time)


def get_period_name(time: int):
    return {
        time <= 45: "1-й тайм",
        45 < time <= 90: "2-й тайм",
        90 < time: "Дополнительное время"
    }[True]


def is_2_element(elements: list) -> bool:
    return len(elements) == 2


def get_substitution_name(element) -> list:
    substitution = element.find_all('span', templates.period_row_substitution_name)
    player_ids = []
    for sub in substitution:
        player_ids += helpers.get_id_of_clickable_element(sub)

    return player_ids


def get_participant_name(element):
    player_name = element.find('span', templates.period_row_participant_name)
    player_ids = []
    if player_name:
        player_ids = helpers.get_id_of_clickable_element(player_name)

    return player_ids


def get_referee_info(match_soup):
    match_info = match_soup.find('div', templates.match_info)
    match_info_content = match_info.find_all('div', templates.match_info_content)
    full_name = match_info_content[0].get_text().split()
    return full_name[2], full_name[1]


def get_match_teams(bot, match_soup, debug=0):

    teams_block = match_soup.find('div', templates.match_info_teams_block)
    teams_soup = teams_block.find_all('div', templates.match_info_teams)

    # team_ids = [helpers.get_id_of_clickable_element(teams_soup[i]) for i in range(2)]
    teams = []

    teams_urls = bot.driver.find_elements_by_class_name(templates.match_info_teams_element)

    for i in range(2):
        sleep(2)
        teams_urls[i + 1].click()
        sleep(2)
        teams.append(get_match_team(bot))

    if debug:
        [print("Team{ind}: {team}".format(ind=i+1, team=teams[i])) for i in range(2)]


@helpers.go_to_a_new_page
def get_match_team(bot):
    match_team = team_info.get_team_info(bot)
    return match_team


def get_match_lineups(bot, debug=0):
    match_soup = bot.get_page_source_by_new_url(helpers.change_js_suffix_in_url(
        bot.driver.current_url, templates.match_info_lineups_js), True)

    lineups_data = match_soup.find('table', templates.match_info_lineups)
    all_players = lineups_data.find('tbody').find_all('tr')

    for row in all_players:
        player_ids = []
        cells = row.find_all('td')

        if templates.match_info_lineups_header in cells[0]['class']:
            continue

        number_1 = cells[0].find('div', templates.match_info_lineups_number).get_text()
        number_2 = cells[1].find('div', templates.match_info_lineups_number).get_text()

        player_ids += helpers.get_id_of_clickable_element(cells[0].find('div', templates.match_info_lineups_player))
        player_ids += helpers.get_id_of_clickable_element(cells[1].find('div', templates.match_info_lineups_player))

        players = []

        for p_url in helpers.convert_ids_to_urls(player_ids):
            player_info_page = bot.get_page_source_by_new_url(p_url)
            players.append(player_info.get_player_info(player_info_page, True))

        if debug:
            print("Игрок1: {player}".format(player=players[0]))
            print("Номер: {number}".format(number=number_1))
            print("Игрок2: {player}".format(player=players[1]))
            print("Номер: {number}".format(number=number_2))
            print()


def get_match_info(bot, debug=0):
    match_events = []

    try:
        match_soup = bot.get_page_source_by_new_url(bot.driver.current_url)

        match_data = match_soup.find('div', templates.periods_block)

        get_match_teams(bot, match_soup, 1)  # debug
        get_match_lineups(bot, 1)  # debug

        referee_full_name = get_referee_info(match_soup)
        if debug:
            print(bot.driver.current_url)
            print("Судья: {referee[1]} {referee[0]}".format(referee=referee_full_name))

        for ev in match_data.find_all('div', templates.period_row):
            player_ids = []

            period_name, time = parse_match_time(ev.find('div', templates.period_row_time).text)

            soccer_ball = ev.find('div', templates.period_row_soccer_ball)
            penalty_missed = ev.find('span', templates.period_row_penalty_missed)
            y_card = ev.find('div', templates.period_row_y_card)
            r_card = ev.find('div', templates.period_row_r_card)
            sub_incident = ev.find('span', templates.period_row_sub_incident_name)
            player_ids += get_substitution_name(ev)
            player_ids += get_participant_name(ev)

            players = []

            for p_url in helpers.convert_ids_to_urls(player_ids):
                player_info_page = bot.get_page_source_by_new_url(p_url)
                players.append(player_info.get_player_info(player_info_page))

            incident = ""
            incident_card = ""
            if y_card:
                incident_card = 'Желтая карточка'
            if r_card:
                incident_card = 'Красная карточка'
            if penalty_missed:
                incident = 'Незабитый пенальти'
            if soccer_ball:
                incident = 'Гол'
            if sub_incident:
                incident = sub_incident.get_text()[1:-1]
            if is_2_element(players):
                incident = 'Замена'

            match_event_data = [period_name, time, incident]
            match_event_data_txt = ['Period', 'Time', 'Event_Type']

            if incident_card:
                match_event_data.append(incident_card)
                match_event_data_txt.append('Card_Type')

            if is_2_element(players):
                match_event_data.append([{'Player_From': players[1], 'Player_To': players[0]}])
                match_event_data_txt.append('Role_Change')
            else:
                match_event_data.append(players[0])
                match_event_data_txt.append('Player')

            match_event = dict(zip(match_event_data_txt, match_event_data))

            match_events.append(match_event)
            if debug:
                print(match_event)
                print("Тайм: {period_name}".format(period_name=period_name))
                print("Время: {time} мин".format(time=time))
                if incident:
                    print("Инцидент: {incident}".format(incident=incident))
                if incident_card:
                    print("Получена {card}".format(card=incident_card))
                if is_2_element(players):
                    print("Игрок вышел на поле: {player}".format(player=players[0]))
                    print("Игрок ушел с поля: {player}".format(player=players[1]))
                else:
                    print("Игрок: {player}".format(player=players[0]))
                print()

    except BaseException as e:
        print("Error: ", e)
        print("Url: ", bot.driver.current_url)

    return match_events


def main():
    match_url = 'https://www.myscore.com.ua/match/EezaGZxc/#match-summary'
    bot = start.Bot(match_url)
    get_match_info(bot, 1)


if __name__ == '__main__':
    main()
