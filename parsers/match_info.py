from myscore_parser import templates
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
