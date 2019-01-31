# project/api/base.py


from flask import Blueprint, jsonify

from project.api.utils import authenticate


base_blueprint = Blueprint('base', __name__)


@base_blueprint.route('/base/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
