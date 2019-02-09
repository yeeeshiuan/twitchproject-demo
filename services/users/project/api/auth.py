from flask import Blueprint, jsonify, request
from sqlalchemy import exc, or_

from project.api.utils import authenticate
from project.api.models import UserSSO
from project import db, bcrypt

auth_blueprint = Blueprint('auth', __name__)


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
        # check for existing user
        user = UserSSO.query.filter(
            or_(UserSSO.twitch_id == twitch_id, UserSSO.email == email)).first()

        if not user:
            # add new user to db
            user = UserSSO(
                twitch_id=twitch_id,
                username=username,
                email=email,
                picture=picture
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

    user = UserSSO.query.filter_by(id=resp).first()

    response_object = {
        'status': 'success',
        'data': user.to_json()
    }
    return jsonify(response_object), 200
