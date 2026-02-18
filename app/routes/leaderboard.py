from flask import Blueprint, render_template
from flask_login import login_required, current_user
import random

leaderboard_bp = Blueprint('leaderboard', __name__)

FAKE_USERS = [
    ('AceStudier', random.randint(2000, 9500)),
    ('BrainWave', random.randint(2000, 9500)),
    ('CardMaster', random.randint(2000, 9500)),
    ('DeckPro', random.randint(2000, 9500)),
    ('FlashKing', random.randint(2000, 9500)),
    ('MemoryLord', random.randint(2000, 9500)),
    ('NeuralNet99', random.randint(2000, 9500)),
    ('QuizWhiz', random.randint(2000, 9500)),
    ('RecallGuru', random.randint(2000, 9500)),
    ('StudyBot3000', random.randint(2000, 9500)),
    ('SynapseX', random.randint(2000, 9500)),
    ('ThinkTank', random.randint(2000, 9500)),
    ('TopNotch', random.randint(2000, 9500)),
    ('WisdomTree', random.randint(2000, 9500)),
    ('ZenLearner', random.randint(2000, 9500)),
]


@leaderboard_bp.route('/leaderboard')
@login_required
def leaderboard():
    # Include current user with a real-ish score
    user_score = current_user.total_cards_studied() * 10 + int(current_user.accuracy_rate() * 20)

    entries = list(FAKE_USERS) + [(current_user.username, user_score)]
    entries.sort(key=lambda x: x[1], reverse=True)

    leaderboard_data = []
    for rank, (name, score) in enumerate(entries, 1):
        leaderboard_data.append({
            'rank': rank,
            'username': name,
            'score': score,
            'is_current_user': name == current_user.username
        })

    return render_template('leaderboard.html', leaderboard=leaderboard_data)
