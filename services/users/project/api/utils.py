from functools import wraps
from flask import request, jsonify
import sys

from project.api.models import UserSSO


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
        if login_type == "sso":
            resp = UserSSO.decode_auth_token(auth_token)
        else:
            response_object['message'] = 'Provide a valid login type.'
            return jsonify(response_object), 403

        if isinstance(resp, str):
            response_object['message'] = resp
            return jsonify(response_object), 401

        return f(resp, login_type, *args, **kwargs)

    return decorated_function
