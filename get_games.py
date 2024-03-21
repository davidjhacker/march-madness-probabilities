import requests
import json

def get_live_games():
    boxscore_endpoint = 'https://ncaa-api.henrygd.me/scoreboard/basketball-men/d1'
    boxscore_response = requests.get(boxscore_endpoint)

    if boxscore_response.status_code == 200:
        games = boxscore_response.json()
    else:
        return f"Error: {boxscore_response.status_code}"
    with open('jsonformatter.txt', 'r') as team_map:  # Ensure this is the correct path to your JSON file.
      TEAM_MAP = json.load(team_map)

    def process_score(score):
        if score == '':
            return 0
        else:
            return score
    def process_half(half):
        if half == '':
            return 'PREGAME'
        else:
            return half
    
    def process_clock(clock):
        if clock == '':
            return '20:00'
        else:
            return clock

    live_games = [
      {
        't1': TEAM_MAP[g['game']['home']['names']['seo']],
        't2': TEAM_MAP[g['game']['away']['names']['seo']],
        'score1': process_score(g['game']['home']['score']),
        'score2': process_score(g['game']['away']['score']),
        'half': process_half(g['game']['currentPeriod']),
        'clock': process_clock(g['game']['contestClock'])
      } for g in games['games'] if g['game']['videoState'] == 'live']

    return live_games