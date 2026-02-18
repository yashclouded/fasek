# FlashForge ⚡

A smart flashcard learning platform built with Flask. Uses spaced repetition to help you master any subject.

## Features

- **User Authentication** — Signup, login, logout with session management
- **Deck Management** — Create, edit, delete flashcard decks
- **Card Management** — Add, edit, delete cards with question + answer pairs
- **Quiz Mode** — Flip-card quiz with Easy / Medium / Hard rating
- **Spaced Repetition** — SM-2 inspired algorithm; hard cards appear more often
- **Performance Dashboard** — Track accuracy, review count, and weakest cards
- **Leaderboard** — Compete against other learners (simulated)

## Tech Stack

| Layer     | Technology              |
|-----------|------------------------|
| Backend   | Flask (Python)          |
| Database  | SQLite + SQLAlchemy     |
| Auth      | Flask-Login + Werkzeug  |
| Frontend  | Jinja2 + Tailwind CSS (CDN) |

## Database Schema

```
users
├── id (PK)
├── username (unique)
├── email (unique)
├── password_hash
└── created_at

decks
├── id (PK)
├── title
├── description
├── user_id (FK → users)
├── created_at
└── updated_at

cards
├── id (PK)
├── question
├── answer
├── deck_id (FK → decks)
├── ease_factor (spaced rep)
├── interval_days
├── next_review
├── review_count
└── created_at

card_reviews
├── id (PK)
├── card_id (FK → cards)
├── difficulty (easy/medium/hard)
└── reviewed_at
```

## Pages

| Route               | Description                     |
|---------------------|---------------------------------|
| `/`                 | Landing page                    |
| `/login`            | Login form                      |
| `/register`         | Signup form                     |
| `/dashboard`        | User dashboard with stats       |
| `/deck/<id>`        | View deck and its cards         |
| `/quiz/<deck_id>`   | Quiz mode for a deck            |
| `/leaderboard`      | Weekly leaderboard              |

## Setup

```bash
# Clone / navigate to project
cd fasek

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

Then open [http://localhost:5001](http://localhost:5001) in your browser.

## Project Structure

```
fasek/
├── run.py                  # Entry point
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py         # App factory + config
│   ├── models.py           # SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py         # Login / register / logout
│   │   ├── main.py         # Landing page + dashboard
│   │   ├── decks.py        # Deck CRUD
│   │   ├── cards.py        # Card CRUD
│   │   ├── quiz.py         # Quiz mode + reviews
│   │   └── leaderboard.py  # Fake leaderboard
│   └── templates/
│       ├── base.html       # Layout with nav + Tailwind
│       ├── landing.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── deck_form.html
│       ├── deck_view.html
│       ├── card_form.html
│       ├── quiz.html
│       ├── quiz_results.html
│       └── leaderboard.html
```

## Quiz Keyboard Shortcuts

| Key       | Action       |
|-----------|-------------|
| Space/Enter | Show answer |
| 1         | Rate Hard    |
| 2         | Rate Medium  |
| 3         | Rate Easy    |
