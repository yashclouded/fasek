from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Deck, Card, CardReview
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return render_template('landing.html', logged_in=True)
    return render_template('landing.html', logged_in=False)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    decks = Deck.query.filter_by(user_id=current_user.id).order_by(Deck.updated_at.desc()).all()

    total_cards = sum(d.card_count() for d in decks)
    total_reviews = current_user.total_cards_studied()
    accuracy = current_user.accuracy_rate()

    # Weakest cards: cards with most "hard" reviews
    weak_cards = []
    all_cards = Card.query.join(Deck).filter(Deck.user_id == current_user.id).all()
    for card in all_cards:
        hard_count = CardReview.query.filter_by(card_id=card.id, difficulty='hard').count()
        total = CardReview.query.filter_by(card_id=card.id).count()
        if total > 0:
            weak_cards.append({
                'card': card,
                'deck_title': card.deck.title,
                'hard_ratio': hard_count / total,
                'hard_count': hard_count,
                'total': total
            })
    weak_cards.sort(key=lambda x: x['hard_ratio'], reverse=True)
    weak_cards = weak_cards[:5]

    return render_template('dashboard.html',
                           decks=decks,
                           total_cards=total_cards,
                           total_reviews=total_reviews,
                           accuracy=accuracy,
                           weak_cards=weak_cards)
