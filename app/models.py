from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    decks = db.relationship('Deck', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def total_cards_studied(self):
        return CardReview.query.join(Card).join(Deck).filter(Deck.user_id == self.id).count()

    def accuracy_rate(self):
        reviews = CardReview.query.join(Card).join(Deck).filter(Deck.user_id == self.id).all()
        if not reviews:
            return 0
        easy_count = sum(1 for r in reviews if r.difficulty == 'easy')
        return round((easy_count / len(reviews)) * 100, 1)


class Deck(db.Model):
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cards = db.relationship('Card', backref='deck', lazy=True, cascade='all, delete-orphan')

    def card_count(self):
        return len(self.cards)

    def mastery_score(self):
        if not self.cards:
            return 0
        scores = []
        for card in self.cards:
            last_review = CardReview.query.filter_by(card_id=card.id).order_by(
                CardReview.reviewed_at.desc()
            ).first()
            if last_review:
                if last_review.difficulty == 'easy':
                    scores.append(100)
                elif last_review.difficulty == 'medium':
                    scores.append(60)
                else:
                    scores.append(20)
            else:
                scores.append(0)
        return round(sum(scores) / len(scores), 1)


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ease_factor = db.Column(db.Float, default=2.5)
    interval_days = db.Column(db.Integer, default=0)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    review_count = db.Column(db.Integer, default=0)

    reviews = db.relationship('CardReview', backref='card', lazy=True, cascade='all, delete-orphan')

    def update_spaced_repetition(self, difficulty):
        """Simple SM-2 inspired spaced repetition logic."""
        now = datetime.utcnow()
        self.review_count += 1

        if difficulty == 'easy':
            self.ease_factor = min(self.ease_factor + 0.15, 3.0)
            if self.interval_days == 0:
                self.interval_days = 1
            elif self.interval_days == 1:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.ease_factor)
        elif difficulty == 'medium':
            self.ease_factor = max(self.ease_factor - 0.05, 1.3)
            if self.interval_days == 0:
                self.interval_days = 1
            else:
                self.interval_days = max(1, int(self.interval_days * 0.8))
        else:  
            self.ease_factor = max(self.ease_factor - 0.2, 1.3)
            self.interval_days = 1

        self.next_review = now + timedelta(days=self.interval_days)

    def difficulty_label(self):
        last = CardReview.query.filter_by(card_id=self.id).order_by(
            CardReview.reviewed_at.desc()
        ).first()
        return last.difficulty if last else 'unreviewed'


class CardReview(db.Model):
    __tablename__ = 'card_reviews'

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)  
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
