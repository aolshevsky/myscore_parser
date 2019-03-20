from myscore_parser import templates
from myscore_parser import storage
from myscore_parser.parsers import match_info, helpers
from time import sleep
import re


def is_start_new_tournament(cell_text: str) -> bool:
    return cell_text.startswith('Тур')


def is_home_team(team_cell) -> bool:
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
    l_time = list(map(lambda x: int(x), reg.findall(date)))
    l_time_str = list(reg.findall(date))
    if l_time[1] > 7:
        return '-'.join([years[0], l_time_str[1], l_time_str[0]]) + 'T{0}:{1}:00.000'.format(l_time_str[2], l_time_str[3])

    return '-'.join([years[1], l_time_str[1], l_time_str[0]]) + 'T{0}:{1}:00.000'.format(l_time_str[2], l_time_str[3])


def update_bad_parse_date_to_site_format(date: str, years: tuple) -> str:
    reg = re.compile(r'[0-9]+')
    l_time = list(map(lambda x: int(x), reg.findall(date)))
    if l_time[1] > 7:
        return date[:6] + years[0] + date[6:]
    return date[:6] + years[1] + date[6:]


@helpers.go_to_a_new_page
def get_match_events(bot, share_data, debug=0):
    match_events = match_info.get_match_info(bot, share_data, debug)  # debug
    return match_events


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
            site_date = update_bad_parse_date_to_site_format(cells[1].get_text(), years)
            home_team = set_home_team(cells[2:4])
            first_team = parse_team_name(cells[2].get_text())
            second_team = parse_team_name(cells[3].get_text())
            score = parse_team_name(cells[4].get_text())
            matches.append(dict(zip(tournament_names, [date, home_team, first_team, second_team, score])))

            match_events_file_name = "match_events_" + '__'.join([site_date, first_team, second_team])
            if not storage.is_file_in_project_dir(match_events_file_name, templates.match_event_folder):
                element = bot.driver.find_element_by_id(row['id'])
                sleep(2)
                element.click()
                sleep(2)
                share_data = {'Date': (date, site_date), 'Home_Team': home_team}
                match_events = get_match_events(bot, share_data,  1)  # debug
                storage.save_to_json_file(match_events, match_events_file_name, templates.match_event_folder)

            if debug:
                print('Дата: {date}'.format(date=date))
                print('Домашняя команда: {home_team}'.format(home_team=home_team))
                print('Команда1: {first_team}'.format(first_team=first_team))
                print('Команда2: {second_team}'.format(second_team=second_team))
                print('Счёт: {score}\n'.format(score=score))

    except BaseException as e:
        print(e)
        return

    tournaments.append(matches)
    return tournaments
