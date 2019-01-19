from flask import Blueprint, jsonify, request
from sqlalchemy import exc, or_
import sys

from project.api.utils import authenticate
from project.api.models import User, UserSSO
from project import db, bcrypt

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/register', methods=['POST'])
def register_user():
    # get post data
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }

    print(post_data, file=sys.stderr)

    if not post_data:
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        # check for existing user
        user = User.query.filter(
            or_(User.username == username, User.email == email)).first()
        if not user:
            # add new user to db
            user = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(user)
            db.session.commit()
            # generate auth token
            auth_token = user.encode_auth_token(user.id)
            response_object['status'] = 'success'
            response_object['message'] = 'Successfully registered.'
            response_object['auth_token'] = auth_token.decode()
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That user already exists.'
            return jsonify(response_object), 400
    # handler errors
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return jsonify(response_object), 400

@auth_blueprint.route('/auth/twitchRegister', methods=['POST'])
def twitch_Register():
    # get post data
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }

    if not post_data:
        return jsonify(response_object), 400

    twitch_id = post_data.get('twitch_id')
    username = post_data.get('username')
    email = post_data.get('email')
    picture = post_data.get('picture')
    try:
        print(f'try start', file=sys.stderr)
        # check for existing user
        user = UserSSO.query.filter(
            or_(UserSSO.twitch_id == twitch_id, UserSSO.email == email)).first()
        print(f'try after query', file=sys.stderr)
        if not user:
            print(f'try if start', file=sys.stderr)
            # add new user to db
            user = UserSSO(
                twitch_id=twitch_id,
                username=username,
                email=email,
                picture=picture
            )
            print(f'try after if', file=sys.stderr)
            print(f'{user}', file=sys.stderr)
            db.session.add(user)
            print(f'try after if and add', file=sys.stderr)
            db.session.commit()

            response_object['message'] = 'Successfully registered.'

        else:
            response_object['message'] = 'Already registered.'

        # generate auth token
        auth_token = user.encode_auth_token(user.id)
        response_object['status'] = 'success'
        response_object['auth_token'] = auth_token.decode()
        return jsonify(response_object), 201
    # handler errors
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return jsonify(response_object), 400

@auth_blueprint.route('/auth/googleRegister', methods=['POST'])
def google_Register():
    # get post data
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    print(f'google:{post_data}', file=sys.stderr)

    if not post_data:
        return jsonify(response_object), 400

    google_id = post_data.get('google_id')
    username = post_data.get('username')
    email = post_data.get('email')
    picture = post_data.get('picture')
    locale = post_data.get('locale')
    try:
        # check for existing user
        user = UserSSO.query.filter(
            or_(UserSSO.google_id == google_id, UserSSO.email == email)).first()
        if not user:
            # add new user to db
            user = UserSSO(
                google_id=google_id,
                username=username,
                email=email,
                picture=picture,
                locale=locale
            )
            db.session.add(user)
            db.session.commit()

            response_object['message'] = 'Successfully registered.'
        else:
            response_object['message'] = 'Already registered.'

        # generate auth token
        auth_token = user.encode_auth_token(user.id)
        response_object['status'] = 'success'
        response_object['auth_token'] = auth_token.decode()
        return jsonify(response_object), 201
    # handler errors
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return jsonify(response_object), 400

@auth_blueprint.route('/auth/login', methods=['POST'])
def login_user():
    # get post data
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        # fetch the user data
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                response_object['status'] = 'success'
                response_object['message'] = 'Successfully logged in.'
                response_object['auth_token'] = auth_token.decode()
                return jsonify(response_object), 200
        else:
            response_object['message'] = 'User does not exist.'
            return jsonify(response_object), 404
    except Exception as e:
        response_object['message'] = 'Try again.'
        return jsonify(response_object), 500


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout_user(resp, login_type):
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    return jsonify(response_object), 200


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def get_user_status(resp, login_type):
    print("users auth status start", file=sys.stderr)
    user = User.query.filter_by(id=resp).first() if login_type == "normal" else UserSSO.query.filter_by(id=resp).first()

    print(f"users auth user={user}", file=sys.stderr)
    response_object = {
        'status': 'success',
        'message': 'success',
        'data': user.to_json()
    }
    return jsonify(response_object), 200
