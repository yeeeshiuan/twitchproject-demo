import datetime
import jwt

from flask import current_app

from project import db, bcrypt

from sqlalchemy.sql import func


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, username, email, password, admin=False):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password,
            current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.admin = admin

    def encode_auth_token(self, user_id):
        """Generates the auth token"""
        try:
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
        except Exception as e:
            return e

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
            'username': self.username,
            'email': self.email,
            'active': self.active,
            'admin': self.admin
        }


class UserSSO(db.Model):
    __tablename__ = 'users_sso'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    twitch_id = db.Column(db.String(64))
    google_id = db.Column(db.String(64))
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    picture = db.Column(db.String(255))

    def __init__(self, username, email, picture, twitch_id="", google_id=""):
        self.google_id = google_id
        self.twitch_id = twitch_id
        self.username = username
        self.email = email
        self.picture = picture

    def encode_auth_token(self, user_id):
        """Generates the auth token"""
        try:
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
        except Exception as e:
            return e

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
        if (self.twitch_id != ""):
            return {
                'id': self.id,
                'twitch_id': self.twitch_id,
                'username': self.username,
                'email': self.email,
                'picture': self.picture
            }
        else:
            return {
                'id': self.id,
                'google_id': self.google_id,
                'username': self.username,
                'email': self.email,
                'picture': self.picture
            }
