from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Deck, Card
from app import db

cards_bp = Blueprint('cards', __name__)


@cards_bp.route('/deck/<int:deck_id>/card/new', methods=['GET', 'POST'])
@login_required
def add_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()

        if not question or not answer:
            flash('Both question and answer are required.', 'error')
            return render_template('card_form.html', deck=deck, card=None)

        card = Card(question=question, answer=answer, deck_id=deck.id)
        db.session.add(card)
        db.session.commit()
        flash('Card added!', 'success')

        # Check if user wants to add another
        if request.form.get('add_another'):
            return redirect(url_for('cards.add_card', deck_id=deck.id))
        return redirect(url_for('decks.view_deck', id=deck.id))

    return render_template('card_form.html', deck=deck, card=None)


@cards_bp.route('/card/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_card(id):
    card = Card.query.get_or_404(id)
    deck = card.deck
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()

        if not question or not answer:
            flash('Both question and answer are required.', 'error')
            return render_template('card_form.html', deck=deck, card=card)

        card.question = question
        card.answer = answer
        db.session.commit()
        flash('Card updated!', 'success')
        return redirect(url_for('decks.view_deck', id=deck.id))

    return render_template('card_form.html', deck=deck, card=card)


@cards_bp.route('/card/<int:id>/delete', methods=['POST'])
@login_required
def delete_card(id):
    card = Card.query.get_or_404(id)
    deck = card.deck
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    db.session.delete(card)
    db.session.commit()
    flash('Card deleted.', 'info')
    return redirect(url_for('decks.view_deck', id=deck.id))
