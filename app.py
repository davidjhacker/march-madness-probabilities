from flask import Flask, request, jsonify, render_template
from scipy.stats import skellam
import json

app = Flask(__name__)

with open ('ratings.json', 'r') as ratings_file:
  rating_dict = json.load(ratings_file)
def midgame_win_prob(score1, score2, r1, r2, portion_of_game_elapsed):
  score_diff = score1 - score2
  print(score_diff)
  r1_adj, r2_adj = r1 * (1 - portion_of_game_elapsed), r2 * (1 - portion_of_game_elapsed)
  print(r1)
  print(r1_adj)
  #For team one to win, the future score diff must be above the negative current score diff. Otherwise, team two wins

  prob_below_neg_diff = skellam.cdf(0 - score_diff - 1, r1_adj, r2_adj)
  prob_above_neg_diff = 1 - skellam.cdf(0 - score_diff, r1_adj, r2_adj)
  #return prob team 1 wins
  return prob_above_neg_diff / (prob_above_neg_diff + prob_below_neg_diff)

def t_midgame_win_prob(t1, t2, score1, score2, portion_of_game_elapsed):
  r1 = rating_dict[t1]
  r2 = rating_dict[t2]
  return midgame_win_prob(score1, score2, r1, r2, portion_of_game_elapsed)
@app.route('/')
def home():
    with open('ratings.json', 'r') as ratings_file:
        rating_dict = json.load(ratings_file)
    team_names = list(rating_dict.keys())  # Extracting team names from the dictionary keys
    return render_template('index.html', team_names=team_names)
@app.route('/run-function', methods=['POST'])
def run_function():
    print(request)
    data = request.json
    result = t_midgame_win_prob(data['team1'], data['team2'], data['score1'], data['score2'], data['portion_elapsed'])
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)