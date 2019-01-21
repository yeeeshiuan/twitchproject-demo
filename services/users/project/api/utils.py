from functools import wraps
from flask import request, jsonify
import sys

from project.api.models import User, UserSSO


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify(response_object), 403

        login_type = request.headers.get('LoginType')
        if not login_type:
            response_object['message'] = 'There is no login type.'
            return jsonify(response_object), 403

        auth_token = auth_header.split(" ")[1]
        resp = None
        if login_type == "normal":
            resp = User.decode_auth_token(auth_token)
        else:
            resp = UserSSO.decode_auth_token(auth_token)

        if isinstance(resp, str):
            response_object['message'] = resp
            return jsonify(response_object), 401

        user = None
        if login_type == "normal":
            user = User.query.filter_by(id=resp).first()
        else:
            user = UserSSO.query.filter_by(id=resp).first()

        if not user or not user.active:
            return jsonify(response_object), 401
        return f(resp, login_type, *args, **kwargs)

    return decorated_function


def is_admin(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.admin
