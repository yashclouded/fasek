from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Deck, Card, CardReview
from app import db
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/quiz/<int:deck_id>')
@login_required
def start_quiz(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    if not deck.cards:
        flash('This deck has no cards. Add some cards first!', 'error')
        return redirect(url_for('decks.view_deck', id=deck.id))

    # Spaced repetition: prioritize cards due for review
    now = datetime.utcnow()
    due_cards = [c for c in deck.cards if c.next_review <= now]
    not_due = [c for c in deck.cards if c.next_review > now]

    # Sort due cards: hard cards first (lower ease_factor), then by next_review
    due_cards.sort(key=lambda c: (c.ease_factor, c.next_review))

    # If fewer than 5 due cards, add some not-due ones
    cards = due_cards
    if len(cards) < len(deck.cards):
        remaining = [c for c in not_due if c not in cards]
        remaining.sort(key=lambda c: c.next_review)
        cards.extend(remaining)

    card_data = [{
        'id': c.id,
        'question': c.question,
        'answer': c.answer,
        'review_count': c.review_count
    } for c in cards]

    return render_template('quiz.html', deck=deck, cards=card_data)


@quiz_bp.route('/quiz/review', methods=['POST'])
@login_required
def review_card():
    card_id = request.form.get('card_id', type=int)
    difficulty = request.form.get('difficulty', '')

    if not card_id or difficulty not in ('easy', 'medium', 'hard'):
        return jsonify({'error': 'Invalid request'}), 400

    card = Card.query.get_or_404(card_id)
    if card.deck.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    # Record review
    review = CardReview(card_id=card.id, difficulty=difficulty)
    db.session.add(review)

    # Update spaced repetition
    card.update_spaced_repetition(difficulty)
    db.session.commit()

    return jsonify({
        'success': True,
        'next_review': card.next_review.strftime('%Y-%m-%d'),
        'interval': card.interval_days
    })


@quiz_bp.route('/quiz/<int:deck_id>/results')
@login_required
def quiz_results(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    return render_template('quiz_results.html', deck=deck)
