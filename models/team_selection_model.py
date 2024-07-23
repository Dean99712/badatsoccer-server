# from flask_sqlalchemy import SQLAlchemy
# from app import app
#
# db = SQLAlchemy(app)
#
#
from django import db


class TeamSelection(db.Model):
    __tablename__ = 'team_selection'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(50), index=True, unique=False)
    team = db.Column(db.String(50), index=True, unique=False)
    stamina = db.Column(db.Integer, index=True, unique=False)
    technique = db.Column(db.Integer, index=True, unique=False)
    ball_leader = db.Column(db.Integer, index=True, unique=False)
    aggression = db.Column(db.Integer, index=True, unique=False)
    tournament = db.Column(db.String(50), index=True, unique=False)
    version = db.Column(db.String(50), index=True, unique=False)
    tournament_to_pick = db.Column(db.String(50), index=True, unique=False)
    team_to_pick = db.Column(db.String(50), index=True, unique=False)
    field_auto = db.Column(db.String(50), index=True, unique=False)
    date = db.Column(db.String(50), index=True, unique=False)
#
#     def __repr__(self):
#         return '<TeamSelection %r>' % self.name
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class PlayerImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    player = db.relationship('Player', backref=db.backref('images', lazy=True))
