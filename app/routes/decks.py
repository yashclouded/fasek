from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Deck, Card
from app import db

decks_bp = Blueprint('decks', __name__)


@decks_bp.route('/deck/new', methods=['GET', 'POST'])
@login_required
def create_deck():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Deck title is required.', 'error')
            return render_template('deck_form.html', deck=None)

        deck = Deck(title=title, description=description, user_id=current_user.id)
        db.session.add(deck)
        db.session.commit()
        flash('Deck created!', 'success')
        return redirect(url_for('decks.view_deck', id=deck.id))

    return render_template('deck_form.html', deck=None)


@decks_bp.route('/deck/<int:id>')
@login_required
def view_deck(id):
    deck = Deck.query.get_or_404(id)
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('deck_view.html', deck=deck)


@decks_bp.route('/deck/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deck(id):
    deck = Deck.query.get_or_404(id)
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Deck title is required.', 'error')
            return render_template('deck_form.html', deck=deck)

        deck.title = title
        deck.description = description
        db.session.commit()
        flash('Deck updated!', 'success')
        return redirect(url_for('decks.view_deck', id=deck.id))

    return render_template('deck_form.html', deck=deck)


@decks_bp.route('/deck/<int:id>/delete', methods=['POST'])
@login_required
def delete_deck(id):
    deck = Deck.query.get_or_404(id)
    if deck.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    db.session.delete(deck)
    db.session.commit()
    flash('Deck deleted.', 'info')
    return redirect(url_for('main.dashboard'))
