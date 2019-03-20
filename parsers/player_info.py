from myscore_parser import templates, storage
import re


def parse_player_info_birthday(player_info):
    row_birthday = player_info.find('div', templates.player_info_birthdate)
    if row_birthday:
        reg = re.compile(r'[0-9]+')
        b_time = list(reg.findall(row_birthday))
        return '{b_time[1]}.{b_time[0]}.{b_time[2]}'.format(b_time=b_time)


def parse_player_info_fullname(player_info):
    player_name = player_info.find('div', templates.player_info_fullname).get_text()
    full_name = player_name.split('(')[0].split()
    f_name, l_name = ' '.join(full_name[1:]), full_name[0]
    return f_name, l_name


def parse_transfer_team_name(team_name: str):
    return team_name[1:-1]


def get_player_info(player_info_page, is_base_info=True, debug=0):
    player_info = player_info_page.find('div', templates.player_info_block)
    f_name, l_name = parse_player_info_fullname(player_info_page)
    country = player_info.find('div', templates.player_info_country).get_text()
    player_type = player_info.find('div', templates.player_info_type_name).get_text()
    birthday = parse_player_info_birthday(player_info)
    transfers = get_player_transfers(player_info_page)
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
        player_info_data.append(transfers)
        player_info_data_txt.append("Transfers")
    player = dict(zip(player_info_data_txt, player_info_data))
    return player


def get_player_transfers(player_info_page):
    transfers = []
    transfer_names = ['Date', 'Team_From', 'Team_To', 'Transfer_Type']
    try:
        if not player_info_page.find('table', templates.player_info_transfer_table):
            return []
        all_transfers = player_info_page.find('table', templates.player_info_transfer_table).find('tbody').find_all('tr')

        for row in all_transfers:
            cells = row.find_all('td')
            date = cells[0].get_text()
            team_from = parse_transfer_team_name(cells[1].get_text())
            team_to = parse_transfer_team_name(cells[2].get_text())
            transfer_type = cells[3].get_text()
            transfers.append(dict(zip(transfer_names, [date, team_from, team_to, transfer_type])))

    except Exception as e:
        print(e)
        return []

    return transfers


def get_players_data_team(row_player):
    match_players_info_history_txt = ['Country', 'Date']
    player_data_txt = ['Role', 'First_Name', 'Last_Name', 'Birthday', 'Person_Info_History']

    row_players_pih = []
    row_players_list = list(row_player.values())
    row_players_pih.append(dict(zip(match_players_info_history_txt,
                                    [row_players_list[i] for i in [3, 2]])))

    return dict(zip(player_data_txt, ['Player'] + [row_players_list[i] for i in [0, 1, 2]] + row_players_pih))


def save_players_teams(players_teams, match_teams):
    players_team_file_names = ['persons_Players_' + '__'.join(list(match_teams[i].values())) for i in range(2)]
    for i in range(len(players_team_file_names)):
        storage.save_data(players_teams[i], players_team_file_names[i], templates.persons_folder)
