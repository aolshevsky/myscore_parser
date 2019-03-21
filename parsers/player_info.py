from myscore_parser import templates, storage
from myscore_parser.parsers import helpers, team_info


def parse_player_info_birthday(player_info):
    row_birthday = player_info.find('div', templates.player_info_birthdate)
    if row_birthday:
        return helpers.swap_day_month_in_date(row_birthday.text[-12:-2])


def parse_player_info_fullname(player_info):
    player_name = player_info.find('div', templates.player_info_fullname).get_text()
    full_name = player_name.split('(')[0].split()
    f_name, l_name = ' '.join(full_name[1:]), full_name[0]
    return f_name, l_name


def parse_transfer_team_name(team_name: str):
    return team_name[1:-1]


def get_player_info(player_info_page, is_base_info=True, debug=0):
    player_info = player_info_page\
        .find('div', templates.player_info_block)
    f_name, l_name = parse_player_info_fullname(player_info_page)
    country = player_info.find('div', templates.player_info_country).get_text()
    player_type = player_info.find('div', templates.player_info_type_name).get_text()
    birthday = parse_player_info_birthday(player_info)
    transfers = get_player_transfers(player_info_page)
    injuries = get_player_injuries(player_info_page)
    if debug:
        print("Игрок\nИмя: {f_name}\nФамилия: {l_name}".format(f_name=f_name, l_name=l_name))
        print("Страна: {country}".format(country=country))
        print("Дата рождения: {birthday}".format(birthday=birthday))
        print("Тип игрока: {type}".format(type=player_type))
        print("Трансферы: {transfers}".format(transfers=transfers))

    player_info_data = [f_name, l_name, birthday]
    player_info_data_txt = ["First_Name", "Last_Name", "Birthday"]

    if not is_base_info:
        player_info_data.append(country)
        player_info_data_txt.append('Country')
        player_info_data.append(player_type)
        player_info_data_txt.append('Type')
        player_info_data.append(injuries)
        player_info_data_txt.append("Injury")
        player_info_data.append(transfers)
        player_info_data_txt.append("Movement")

    player = dict(zip(player_info_data_txt, player_info_data))
    return player


def get_player_transfers(player_info_page):
    transfers = []
    transfer_names = ['Date', 'TeamFrom', 'TeamTo', 'Type']
    transfer_team_txt = ['Name', 'Country']
    try:
        if not player_info_page.find('table', templates.player_info_transfer_table):
            return []
        all_transfers = player_info_page\
            .find('table', templates.player_info_transfer_table)\
            .find('tbody')\
            .find_all('tr')

        for row in all_transfers:
            cells = row.find_all('td')

            # team_ids = [helpers.get_href_of_element(
            #     cells[i].find('td', templates.player_info_injuries_table_team_name))[1] for i in range(1, 3)]
            #
            # row_teams = []
            #
            # for t_url in helpers.convert_ids_to_urls(team_ids):
            #     row_teams.append(team_info.get_team_info(bot, t_url))
            #     bot.driver.back()

            date = helpers.swap_day_month_in_date(cells[0].get_text())
            team_from = parse_transfer_team_name(cells[1].get_text())
            team_from_data = dict(zip(transfer_team_txt, [team_from, 'No country']))
            team_to = parse_transfer_team_name(cells[2].get_text())
            team_to_data = dict(zip(transfer_team_txt, [team_to, 'No country']))
            team_info.save_team(team_to_data)
            team_info.save_team(team_from_data)
            transfer_type = cells[3].get_text()
            transfers.append(dict(zip(transfer_names, [date, team_from_data, team_to_data, transfer_type])))

    except Exception as e:
        print("Player transfers error:", e)
        return []

    return transfers


def get_player_injuries(player_info_page):
    injuries = []
    injuries_txt = ['Name', 'DateFrom', 'DateTo']
    try:
        if not player_info_page.find('table', templates.player_info_injuries_table):
            return []
        all_injuries = player_info_page\
            .find('table', templates.player_info_injuries_table)\
            .find('tbody')\
            .find_all('tr')

        for row in all_injuries:
            cells = row.find_all('td')
            date_from = helpers.swap_day_month_in_date(cells[0].get_text())
            date_to = helpers.swap_day_month_in_date(cells[1].get_text())
            injury_name = cells[2].get_text()
            injuries.append(dict(zip(injuries_txt, [injury_name, date_from, date_to])))

    except Exception as e:
        print(e)
        return []

    return injuries


def get_players_data_team(row_player, is_full_info=False):
    match_players_info_history_txt = ['Country', 'Date']
    player_data_txt = ['Role', 'First_Name', 'Last_Name', 'Birthday', 'Person_Info_History']

    row_players_add_info = [dict(zip(match_players_info_history_txt,
                                     [row_player['Country'], row_player['Birthday']]))]

    if is_full_info:
        player_data_txt += ['Injury', 'Movement']
        row_players_add_info += [row_player['Injury'], row_player['Movement']]

    return dict(zip(player_data_txt, ['Player'] + [row_player['First_Name'], row_player['Last_Name'],
                                                   row_player['Birthday']] + row_players_add_info))


def save_players_teams(players_teams, match_teams, b_date, folder_name):
    players_team_file_names = ['persons_Players_' + '__'.join(list(match_teams[i].values()) +
                                                              [b_date]) for i in range(2)]
    for i in range(len(players_team_file_names)):
        storage.save_data(players_teams[i], players_team_file_names[i], folder_name)
