# project/api/lexical.py


from flask import Blueprint, jsonify

from project.api.utils import authenticate


lexical_blueprint = Blueprint('lexical', __name__)


@lexical_blueprint.route('/lexical/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@lexical_blueprint.route('/lexical/authping', methods=['GET'])
@authenticate
def ping_authpong(resp, login_type):
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
