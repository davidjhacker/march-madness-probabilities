from flask import Flask, request, jsonify, render_template
from get_games import get_live_games
from scipy.stats import skellam
import threading
import time
import json

app = Flask(__name__)

cached_live_games = {}

with open('formatted_ratings.json', 'r') as ratings_file:  # Ensure this is the correct path to your JSON file.
    rating_dict = json.load(ratings_file)


def midgame_win_prob(score1, score2, r1, r2, portion_of_game_elapsed):
    score_diff = score1 - score2
            
    r1_adj, r2_adj = r1 * (1 - portion_of_game_elapsed), r2 * (1 - portion_of_game_elapsed)
    r1_ot, r2_ot = r1 / 8, r2 / 8
    #for t1 to win in regulation, the score must stay above the current negative score differential
    prob_t1_wins_regulation = 1 - skellam.cdf(0 - score_diff, r1_adj, r2_adj)
    #for a regulation tie, the score diffs must cancel out
    prob_tie_regulation = skellam.pmf(0 - score_diff, r1_adj, r2_adj)
    prob_t1_wins_overtime = 1 - skellam.cdf(0, r1_ot, r2_ot)
    prob_tie_overtime = skellam.pmf(0, r1_ot, r2_ot)
    if portion_of_game_elapsed == 1:
        if score_diff == 0:
            prob_t1_wins_regulation = 0
            prob_tie_regulation = 1
        elif score_diff > 0:
            prob_t1_wins_regulation = 1
            prob_tie_regulation = 0
        elif score_diff < 0:
            prob_t1_wins_regulation = 0
            prob_tie_regulation = 1
    return (prob_t1_wins_regulation * (prob_tie_overtime - 1) - prob_t1_wins_overtime * prob_tie_regulation) / (prob_tie_overtime - 1)

def t_midgame_win_prob(t1, t2, score1, score2, portion_of_game_elapsed):
    r1 = rating_dict[t1]
    r2 = rating_dict[t2]
    return midgame_win_prob(score1, score2, r1, r2, portion_of_game_elapsed)

def update_live_games_cache(interval=10):  # Interval in seconds
    global cached_live_games
    while True:
        try:
            cached_live_games = get_live_games()
            print("Cache updated!")
        except Exception as e:
            print(f"Error updating cache: {e}")
        time.sleep(interval)

@app.route('/')
def home():
    team_names = list(rating_dict.keys())  # Make sure this is after you've loaded rating_dict
    return render_template('index.html', team_names=team_names)

@app.route('/live-games')
def live_games():
    global cached_live_games
    return jsonify(cached_live_games)

@app.route('/run-function', methods=['POST'])
def run_function():
    half_map = {
        '1ST HALF': 1,
        'PREGAME': 1,
        '2ND HALF': 2,
        'END 2ND': 2,
        '': 1,
        'FINAL': 2,
        'HALFTIME': 1,
    }
    data = request.json
    half = int(half_map[data['half']])
    time_on_clock = data['timeOnClock']
    if time_on_clock == '':
        time_on_clock = '20:00'
    score1 = data['score1']
    score2 = data['score2']
    if score1 == '':
        score1 = 0
    if score2 == '':
        score2 = 0
    minutes, seconds = map(int, time_on_clock.split(':'))
    time_elapsed_in_half = 20 - (minutes + seconds / 60.0)
    total_time = 20 * (half - 1) + time_elapsed_in_half  # Adjusted for a total game time of 40 minutes.
    portion_elapsed = total_time / 40.0

    result = t_midgame_win_prob(data['team1'], data['team2'], int(score1), int(score2), portion_elapsed)
    formatted_result = f"{data['team1']} has a {result * 100:.2f}% chance of beating {data['team2']}"
    return jsonify(result=formatted_result)

if __name__ == '__main__':
    # Start the background thread
    updater_thread = threading.Thread(target=update_live_games_cache, args=(5,), daemon=True)
    updater_thread.start()
    
    # Start the Flask app
    app.run(debug=True)