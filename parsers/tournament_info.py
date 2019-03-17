from myscore_parser import templates
from myscore_parser.parsers import match_info
from time import sleep
import re


def is_start_new_tournament(cell_text):
    return cell_text.startswith('Тур')


def is_home_team(team_cell):
    return "team-home" in team_cell['class']


def set_home_team(teams):
    home_team = 'null'
    if is_home_team(teams[0]):
        home_team = parse_team_name(teams[0].get_text())
    if is_home_team(teams[1]):
        home_team = parse_team_name(teams[1].get_text())

    return home_team


def parse_team_name(score):
    return re.sub('[\xa0]', '', score)


def get_tournament_matches(bot, tournament_info_page):
    tournaments, matches = [], []
    tournament_names = ['Date', 'Home_Team', 'First_Team', 'Second_Team', 'Score']
    try:
        transfer_block = tournament_info_page.find('div', templates.tournament_info)
        all_transfers = transfer_block.find('tbody').find_all('tr')
        for row in all_transfers:
            cells = row.find_all('td')
            if is_start_new_tournament(cells[0].get_text()):
                if matches:
                    tournaments.append(matches)
                matches = []
                continue

            date = cells[1].get_text()
            home_team = set_home_team(cells[2:4])
            first_team = parse_team_name(cells[2].get_text())
            second_team = parse_team_name(cells[3].get_text())
            score = parse_team_name(cells[4].get_text())
            matches.append(dict(zip(tournament_names, [date, home_team, first_team, second_team, score])))
            element = bot.driver.find_element_by_id(row['id'])
            element.click()
            sleep(2)
            bot.driver.switch_to.window(bot.driver.window_handles[-1])
            match_info.get_match_info(bot)
            bot.driver.close()
            bot.driver.switch_to.window(bot.window_handle)

    except BaseException as e:
        print(e)
        return

    tournaments.append(matches)
    return tournaments

