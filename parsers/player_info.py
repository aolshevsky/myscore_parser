from myscore_parser import templates


def get_player_info(player_info_page):
    player_info = player_info_page.find('div', templates.player_info_block)
    f_name, l_name = parse_player_info_fullname(player_info_page)
    print("Игрок\nИмя: {f_name}\nФамилия: {l_name}".format(f_name=f_name, l_name=l_name))
    print("Страна: {country}".format(country=player_info.find('div', templates.player_info_country).get_text()))
    print("Дата рождения: {birthday}".format(birthday=parse_player_info_birthday(player_info)))
    print("Тип игрока: {type}".format(type=player_info.find('div', templates.player_info_type_name).get_text()))


def parse_player_info_birthday(player_info):
    row_birthday = player_info.find('div', templates.player_info_birthdate)
    if row_birthday:
        return row_birthday.text[-12:-2]


def parse_player_info_fullname(player_info):
    player_name = player_info.find('div', templates.player_info_fullname).get_text()
    full_name = player_name.split('(')[0].split()
    f_name, l_name = ' '.join(full_name[1:]), full_name[0]
    return f_name, l_name


def parse_transfer_team_name(team_name):
    return team_name[1:-1]


def get_player_transfers(player_info_page):
    transfers = []
    transfer_names = ['Date', 'Team_From', 'Team_To', 'Transfer_Type']
    try:
        all_transfers = player_info_page.find('table', templates.player_info_transfer_table).find('tbody').find_all('tr')

        for row in all_transfers:
            cells = row.find_all('td')
            date = cells[0].get_text()
            team_from = parse_transfer_team_name(cells[1].get_text())
            team_to = parse_transfer_team_name(cells[2].get_text())
            transfer_type = cells[3].get_text()
            transfers.append(dict(zip(transfer_names, [date, team_from, team_to, transfer_type])))

    except:
        return

    return transfers
