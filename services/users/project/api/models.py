import datetime
import jwt

from flask import current_app

from project import db

from sqlalchemy.sql import func


class UserSSO(db.Model):
    __tablename__ = 'users_sso'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    twitch_id = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    picture = db.Column(db.String(255))

    def __init__(self, username, email, picture, twitch_id):
        self.twitch_id = twitch_id
        self.username = username
        self.email = email
        self.picture = picture

    def encode_auth_token(self, user_id):
        """Generates the auth token"""
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                ),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def to_json(self):
        return {
            'id': self.id,
            'twitch_id': self.twitch_id,
            'username': self.username,
            'email': self.email,
            'active': self.active,
            'picture': self.picture
        }
