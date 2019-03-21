from myscore_parser import templates, storage


def get_team__name__country(team_info: str) -> tuple:
    team_info_list = team_info.split()
    return ' '.join(team_info_list[2:]), team_info_list[1]


def get_team_data_by_name(teams_data, team_name):
    for team in teams_data:
        if team['Name'] == team_name:
            return team


def get_team_info(bot, url=""):
    if url:
        get_url = url
    else:
        get_url = bot.driver.current_url
    team_soup = bot.get_page_source_by_new_url(get_url)
    team_info = team_soup.find('h2', templates.team_info_country_name).get_text()
    name, country = get_team__name__country(team_info)

    team_info_data = [name, country]
    team_info_data_txt = ['Name', 'Country']
    team = dict(zip(team_info_data_txt, team_info_data))

    return team


def save_team(team):
    file_name = "team_" + '__'.join(list(team.values()))
    storage.save_data(team, file_name, templates.teams_folder)
