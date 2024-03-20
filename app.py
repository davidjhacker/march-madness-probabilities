from flask import Flask, request, jsonify, render_template
from scipy.stats import skellam
import json

app = Flask(__name__)

with open('formatted_ratings.json', 'r') as ratings_file:  # Ensure this is the correct path to your JSON file.
    rating_dict = json.load(ratings_file)

def midgame_win_prob(score1, score2, r1, r2, portion_of_game_elapsed):
    score_diff = score1 - score2
    r1_adj, r2_adj = r1 * (1 - portion_of_game_elapsed), r2 * (1 - portion_of_game_elapsed)
    
    prob_below_neg_diff = skellam.cdf(0 - score_diff - 1, r1_adj, r2_adj)
    prob_above_neg_diff = 1 - skellam.cdf(0 - score_diff, r1_adj, r2_adj)
    return prob_above_neg_diff / (prob_above_neg_diff + prob_below_neg_diff)

def t_midgame_win_prob(t1, t2, score1, score2, portion_of_game_elapsed):
    r1 = rating_dict[t1]
    r2 = rating_dict[t2]
    return midgame_win_prob(score1, score2, r1, r2, portion_of_game_elapsed)

@app.route('/')
def home():
    team_names = list(rating_dict.keys())  # Make sure this is after you've loaded rating_dict
    return render_template('index.html', team_names=team_names)

@app.route('/run-function', methods=['POST'])
def run_function():
    data = request.json
    half = int(data['half'])
    time_on_clock = data['timeOnClock']
    minutes, seconds = map(int, time_on_clock.split(':'))
    
    total_time = 20 * (half - 1) + minutes + seconds / 60.0  # Adjusted for a total game time of 40 minutes.
    portion_elapsed = total_time / 40.0

    result = t_midgame_win_prob(data['team1'], data['team2'], data['score1'], data['score2'], portion_elapsed)
    formatted_result = f"{data['team1']} has a {result * 100:.2f}% chance of beating {data['team2']}"
    return jsonify(result=formatted_result)

if __name__ == '__main__':
    app.run(debug=True)