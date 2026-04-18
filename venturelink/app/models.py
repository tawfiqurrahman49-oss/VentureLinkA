from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'startup' or 'investor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    swipes_given = db.relationship('Swipe', foreign_keys='Swipe.swiper_id', backref='swiper', lazy='dynamic')
    swipes_received = db.relationship('Swipe', foreign_keys='Swipe.swiped_id', backref='swiped', lazy='dynamic')
    matches_a = db.relationship('Match', foreign_keys='Match.user_a_id', backref='user_a', lazy='dynamic')
    matches_b = db.relationship('Match', foreign_keys='Match.user_b_id', backref='user_b', lazy='dynamic')

    def has_swiped(self, user_id):
        return Swipe.query.filter_by(swiper_id=self.id, swiped_id=user_id).first() is not None

    def is_matched_with(self, user_id):
        return Match.query.filter(
            ((Match.user_a_id == self.id) & (Match.user_b_id == user_id)) |
            ((Match.user_a_id == user_id) & (Match.user_b_id == self.id))
        ).first() is not None


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Startup-specific
    stage = db.Column(db.String(30))         # pre-seed, seed, series-a, etc.
    funding_ask = db.Column(db.String(50))   # e.g. "$500K"
    team_size = db.Column(db.Integer)

    # Investor-specific
    check_size = db.Column(db.String(50))    # e.g. "$50K–$500K"
    thesis = db.Column(db.Text)
    portfolio = db.Column(db.String(300))


class Swipe(db.Model):
    __table_args__ = (db.UniqueConstraint('swiper_id', 'swiped_id'),)
    id = db.Column(db.Integer, primary_key=True)
    swiper_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    swiped_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    direction = db.Column(db.String(4), nullable=False)  # 'left' or 'right'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Match(db.Model):
    __table_args__ = (db.UniqueConstraint('user_a_id', 'user_b_id'),)
    id = db.Column(db.Integer, primary_key=True)
    user_a_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_b_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    match = db.relationship('Match', backref='messages')
    sender = db.relationship('User', backref='sent_messages')