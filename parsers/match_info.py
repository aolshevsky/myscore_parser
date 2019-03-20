from myscore_parser import templates, start, storage
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


def get_referee_info(match_soup, is_inserting=False):
    match_info = match_soup.find('div', templates.match_info)
    match_info_content = match_info.find_all('div', templates.match_info_content)
    full_name = match_info_content[0].get_text().split()
    referee_data = []
    referee_data_txt = []
    if is_inserting:
        referee_data = ['Referee']
        referee_data_txt = ['Role']
    referee_data += [full_name[2], full_name[1]]
    referee_data_txt += ['First_Name', 'Last_Name']

    return dict(zip(referee_data_txt, referee_data))


def save_referee_data(referee):
    referee_file_name = 'persons_' + '__'.join(referee.values())
    storage.save_data(referee, referee_file_name, templates.persons_folder)


def get_match_teams(bot, debug=0):
    teams = []
    teams_urls = bot.driver.find_elements_by_class_name(templates.match_info_teams_element)

    for i in range(2):
        sleep(2)
        teams_urls[i + 1].click()
        sleep(2)
        teams.append(get_match_team(bot))

    if debug:
        [print("Team{ind}: {team}".format(ind=i+1, team=teams[i])) for i in range(2)]

    return teams


@helpers.go_to_a_new_page
def get_match_team(bot):
    match_team = team_info.get_team_info(bot)
    file_name = "team_" + '__'.join(list(match_team.values()))
    storage.save_data(match_team, file_name, templates.teams_folder)
    return match_team


def get_match_lineups(bot, match_teams, match_teams_dict, match_date, debug=0):
    match_soup = bot.get_page_source_by_new_url(helpers.change_js_suffix_in_url(
        bot.driver.current_url, templates.match_info_lineups_js), True)

    lineups_data = match_soup.find('table', templates.match_info_lineups)
    all_players = lineups_data.find('tbody').find_all('tr')
    is_main = 1

    players_data_team1, players_data_team2 = [], []
    match_players_txt = ['First_Name', 'Second_Name', 'Birthday', 'Player_Type', 'Number',
                         'Is_Main', 'First_Team', 'Second_Team']
    match_players = []

    for row in all_players:
        cells = row.find_all('td')

        if templates.match_info_lineups_header in cells[0]['class']:
            if templates.match_info_lineups_header_no_main == cells[0].get_text():
                is_main = 0
            continue

        numbers = [cells[i].find('div', templates.match_info_lineups_number).get_text() for i in range(2)]

        player_ids = [helpers.get_id_of_clickable_element(
            cells[i].find('div', templates.match_info_lineups_player))[0] for i in range(2)]

        row_players = []
        row_match_player = []

        for p_url in helpers.convert_ids_to_urls(player_ids):
            player_info_page = bot.get_page_source_by_new_url(p_url)
            row_players.append(player_info.get_player_info(player_info_page, False))

        players_data_team1.append(player_info.get_players_data_team(row_players[0]))
        players_data_team2.append(player_info.get_players_data_team(row_players[1]))

        row_match_player += [dict(zip(match_players_txt, [list(row_players[i].values())[j] for j in [0, 1, 2, 4]] +
                                      [numbers[i], is_main] + match_teams)) for i in range(2)]
        match_players += row_match_player

        if debug:
            [print("Игрок{ind}: {player}".format(ind=i+1, player=row_players[i])) for i in range(2)]
            [print("Номер{ind}: {number}".format(ind=i+1, number=numbers[i])) for i in range(2)]
            print("Основной состав: {is_main}".format(is_main=is_main))
            print()

    save_match_players(match_players, match_teams_dict, match_date)

    return players_data_team1, players_data_team2


def save_match_referee(match_referee: list, match_date: str):
    match_referee_dict = match_referee[0]
    match_referee_file_name = 'match_referee_' + '__'.join([match_referee_dict['First_Team']['Name'],
                                                            match_referee_dict['Second_Team']['Name'],
                                                            match_date,
                                                            match_referee_dict['Last_Name']])
    storage.save_data(match_referee, match_referee_file_name, templates.match_referee_folder)


def save_match_players(match_players: list, match_teams: dict, match_date: str):
    match_players_file_name = 'match_players_' + '__'.join([match_teams['First_Team']['Name'],
                                                            match_teams['Second_Team']['Name'],
                                                            match_date])
    storage.save_data(match_players, match_players_file_name, templates.match_players_folder)


def save_match(match: list, match_date: str):
    match_dict = match[0]
    match_file_name = 'match_' + '__'.join([match_dict['First_Team']['Name'],
                                            match_dict['Second_Team']['Name'],
                                            match_date])
    storage.save_data(match, match_file_name, templates.match_folder)


def get_match_info(bot, share_data, debug=0):
    try:
        match_soup = bot.get_page_source_by_new_url(bot.driver.current_url)

        match_data = match_soup.find('div', templates.periods_block)

        match_teams = get_match_teams(bot, 1)  # debug

        match_date, site_date = share_data['Date']
        match_data_for_match_events = match_teams + [match_date]
        match_data_for_match_events_txt = ['First_Team', 'Second_Team', 'Date']
        match_for_match_events = dict(zip(match_data_for_match_events_txt, match_data_for_match_events))

        match_cards = []
        match_cards_txt = ['Match_Time_Template_Name', 'Match_Time', 'Player', 'Referee',
                           'Card_Template_Name', 'Description']
        match_role_changes = []
        match_role_changes_txt = ['Match_Time_Template_Name', 'Match_Time', 'Person_To', 'Person_From']
        match_simple_events = []
        match_simple_events_txt = ['Match_Time_Template_Name', 'Match_Time', 'Player', 'Event_Template_Name']
        match_referee_txt = ['First_Name', 'Last_Name', 'First_Team', 'Second_Team', 'Date_Time', 'Is_Main']
        match_referee = []
        match = match_teams
        match += [team_info.get_team_data_by_name(match_teams, share_data['Home_Team'])] + [match_date]
        match_txt = ['First_Team', 'Second_Team', 'Home_Team', 'Date_Time']

        players_teams = get_match_lineups(bot, match_teams, match_for_match_events, site_date, 1)  # debug
        player_info.save_players_teams(players_teams, match_teams, site_date)

        referee = get_referee_info(match_soup)
        match_referee += referee.values()
        match_referee += match_data_for_match_events + [1]
        save_referee_data(get_referee_info(match_soup, True))
        matches = []
        match_referees = []
        matches.append(dict(zip(match_txt, match)))
        match_referees.append(dict(zip(match_referee_txt, match_referee)))
        save_match_referee(match_referees, site_date)
        save_match(matches, site_date)

        if debug:
            print(bot.driver.current_url)

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
                incident_card = 'Желтая'
            if r_card:
                incident_card = 'Красная'
            if penalty_missed:
                incident = 'Незабитый пенальти'
            if soccer_ball:
                incident = 'Гол'
            if sub_incident:
                incident = sub_incident.get_text()[1:-1]
            if is_2_element(players):
                incident = 'Замена'

            if incident_card:
                match_card = [period_name, time, players[0], referee, incident_card, incident]
                match_cards.append(dict(zip(match_cards_txt, match_card)))

            if is_2_element(players):
                match_role_change = [period_name, time, players[0], players[1]]
                match_role_changes.append(dict(zip(match_role_changes_txt, match_role_change)))
            else:
                match_simple_event = [period_name, time, players[0], incident]
                match_simple_events.append(dict(zip(match_simple_events_txt, match_simple_event)))

            if debug:
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

        match_events_data_txt = ['Match', 'Simple_Events', 'Cards', 'Role_Changes']
        match_events_data = [match_for_match_events, match_simple_events, match_cards, match_role_changes]
        match_events = dict(zip(match_events_data_txt, match_events_data))

        return match_events

    except BaseException as e:
        print("Error: ", e)
        print("Url: ", bot.driver.current_url)


def main():
    match_url = 'https://www.myscore.com.ua/match/EezaGZxc/#match-summary'
    bot = start.Bot(match_url)
    get_match_info(bot, "", 1)


if __name__ == '__main__':
    main()
