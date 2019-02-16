# project/api/utils.py
import json
from functools import wraps

import requests
from flask import request, jsonify, current_app


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response_object = {
            'status': 'error',
            'message': 'Something went wrong. Please contact us.'
        }

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            response_object['message'] = 'Provide a valid auth token.'
            return jsonify(response_object), 403

        login_type = request.headers.get('LoginType')
        if not login_type:
            response_object['message'] = 'There is no login type.'
            return jsonify(response_object), 403

        auth_token = auth_header.split(" ")[1]
        response = ensure_authenticated(auth_token, login_type)

        if not response:
            response_object['message'] = 'Invalid token.'
            return jsonify(response_object), 401
        return f(response, login_type, *args, **kwargs)
    return decorated_function


def ensure_authenticated(token, login_type):
    if current_app.config['TESTING']:
        if token == "valid":
            insideData = {"active": True,
                          "email": "test@test.test",
                          "id": 1,
                          "picture": "pictureURL",
                          "twitch_id": "1234567",
                          "username": "test"}
            data = {'status': 'success', 'data': insideData}
            return data
        else:
            return None
    else:

        url = '{0}/auth/status'.format(current_app.config['USERS_SERVICE_URL'])
        bearer = 'Bearer {0}'.format(token)
        headers = {'Authorization': bearer, 'LoginType': login_type}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        if response.status_code == 200 and \
           data['status'] == 'success' and \
           data['data']['active']:
            return data
        else:
            return False
