
def get_player_matches(steam_id, number_of_matches):
    query = f'https://aoe2.net/api/player/matches?game=aoe2de&steam_id={steam_id}&count={number_of_matches}'
    return query
def get_player_history(steam_id, number_of_matches, leaderboard_id):
    query = f'https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id={leaderboard_id}&steam_id={steam_id}&count={number_of_matches}'
    return query
def get_matches(number_of_matches, start_time):
    query = f'https://aoe2.net/api/matches?game=aoe2de&count={number_of_matches}&since={start_time}'
    return query
def get_match_details_match_id(match_id):
    query = f'https://aoe2.net/api/match?match_id={match_id}'
    return query
def get_match_details_uuid(uuid):
    query = f'https://aoe2.net/api/match?uuid={uuid}'
    return query
