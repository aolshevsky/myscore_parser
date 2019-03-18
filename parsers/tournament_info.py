from myscore_parser import templates
from myscore_parser import storage
from myscore_parser.parsers import match_info
from time import sleep
import re


def is_start_new_tournament(cell_text: str) -> bool:
    return cell_text.startswith('Тур')


def is_home_team(team_cell):
    return "team-home" in team_cell['class']


def set_home_team(teams: list) -> str:
    home_team = 'null'
    if is_home_team(teams[0]):
        home_team = parse_team_name(teams[0].get_text())
    if is_home_team(teams[1]):
        home_team = parse_team_name(teams[1].get_text())

    return home_team


def parse_team_name(score: str) -> str:
    return re.sub('[\xa0]', '', score)


def parse_tournament_date(tournament_info_page) -> tuple:
    date = tournament_info_page.find('span', templates.tournament_info_date).get_text().split('/')
    return date[0], date[1]


def update_bad_parse_date(date: str, years: tuple) -> str:
    reg = re.compile(r'[0-9]+')
    list_int_time = list(map(lambda x: int(x), reg.findall(date)))
    if list_int_time[1] > 7:
        return date[:6] + years[0] + date[6:]

    return date[:6] + years[1] + date[6:]


def start_parse_match(bot):
    bot.driver.switch_to.window(bot.driver.window_handles[-1])
    match_events = match_info.get_match_info(bot, 1)  # debug
    end_parse_match(bot)
    return match_events


def end_parse_match(bot):
    bot.driver.close()
    bot.driver.switch_to.window(bot.window_handle)


def get_tournament_matches(bot, tournament_info_page, debug=0):
    tournaments, matches = [], []
    tournament_names = ['Date', 'Home_Team', 'First_Team', 'Second_Team', 'Score']
    try:
        transfer_block = tournament_info_page.find('div', templates.tournament_info)
        all_transfers = transfer_block.find('tbody').find_all('tr')
        years = parse_tournament_date(tournament_info_page)

        for row in all_transfers:
            cells = row.find_all('td')
            if is_start_new_tournament(cells[0].get_text()):
                if matches:
                    tournaments.append(matches)
                matches = []
                continue

            date = update_bad_parse_date(cells[1].get_text(), years)
            home_team = set_home_team(cells[2:4])
            first_team = parse_team_name(cells[2].get_text())
            second_team = parse_team_name(cells[3].get_text())
            score = parse_team_name(cells[4].get_text())
            matches.append(dict(zip(tournament_names, [date, home_team, first_team, second_team, score])))

            element = bot.driver.find_element_by_id(row['id'])
            sleep(2)
            element.click()
            sleep(2)
            match_events = start_parse_match(bot)
            storage.save_to_json_file(match_events,
                                      "match_events_" + '__'.join([date, first_team, second_team]), "match_events")

            if debug:
                print('Дата: {date}'.format(date=date))
                print('Домашняя команда: {home_team}'.format(home_team=home_team))
                print('Команда1: {first_team}'.format(first_team=first_team))
                print('Команда2: {second_team}'.format(second_team=second_team))
                print('Счёт: {score}\n'.format(score=score))

    except BaseException as e:
        # print(e)
        return

    tournaments.append(matches)
    return tournaments
