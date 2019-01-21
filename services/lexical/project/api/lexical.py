# project/api/lexical.py

import sys

from flask import Blueprint, jsonify, request, json

from project.api.utils import authenticate, getAnalyze


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


@lexical_blueprint.route('/lexical/analyze', methods=['POST'])
@authenticate
def analyze(resp, login_type):
    # get post data
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400

    sentence = post_data.get('sentence')
    print(f'sentence={sentence}, dataType={type(sentence)}', file=sys.stderr)

    result = getAnalyze(sentence)
    print(f'result={result}, dataType={type(result)}', file=sys.stderr)

    # If ensure_ascii is false,
    # then the return value will be a unicode instance subject to normal Python str
    # to unicode coercion rules instead of being escaped to an ASCII str.
    return jsonify({
        'status': 'success',
        'message': json.dumps(result, ensure_ascii=False)
    })
