BASE_URL = 'http://www.myscore.com.ua'


tournament_info = {'class', 'tournament-page'}
tournament_info_get_more_matches = "//table[@class='link-more-games']/tbody/tr/td/a"
tournament_info_date = {'class', 'breadcrumb__text'}


match_info = {'class': 'match-information-data'}
match_info_content = {'class', 'content'}
match_info_lineups_js = '#lineups;1'
match_info_lineups = {'class', 'parts'}
match_info_lineups_header = 'h-part'
match_info_lineups_content = {'id', 'tab-match-lineups'}
match_info_lineups_number = {'class', 'time-box'}
match_info_lineups_player = {'class', 'name'}


periods_block = {'class': 'detailMS'}
periods_headers = {'class': 'detailMS__headerText'}
period_row = {'class': 'detailMS__incidentRow'}
period_row_time = {'class': ['time-box', 'time-box-wide']}
period_row_y_card = {'class': 'y-card'}
period_row_r_card = {'class': 'r-card'}
period_row_penalty_missed = {'class': 'penalty-missed'}
period_row_substitution_name = {'class': ['substitution-in-name', 'substitution-out-name']}
period_row_participant_name = {'class': 'participant-name'}
period_row_soccer_ball = {'class': 'soccer-ball'}
period_row_sub_incident_name = {'class': 'subincident-name'}


player_info_block = {'class': 'player-info'}
player_info_fullname = {'class': 'team-name'}
player_info_country = {'class': 'player-country'}
player_info_birthdate = {'class': 'player-birthdate'}
player_info_type_name = {'class': 'player-type-name'}
player_info_transfer_table = {'class': 'transfer-table'}


team_info_country_name = {'class', 'tournament'}
