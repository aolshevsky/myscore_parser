from myscore_parser import templates


def get_team__name__country(team_info: str) -> tuple:
    team_info_list = team_info.split()
    return team_info_list[-1], team_info_list[-2]


def get_team_info(bot):
    team_soup = bot.get_page_source_by_new_url(bot.driver.current_url)
    team_info = team_soup.find('h2', templates.team_info_country_name).get_text()
    name, country = get_team__name__country(team_info)

    team_info_data = [name, country]
    team_info_data_txt = ['Name', 'Country']
    team = dict(zip(team_info_data_txt, team_info_data))

    return team
