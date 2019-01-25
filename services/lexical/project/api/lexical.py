# project/api/lexical.py

import sys

from flask import Blueprint, jsonify, request, json
import jieba.posseg as pseg
from opencc import OpenCC

from project.api.utils import authenticate


lexical_blueprint = Blueprint('lexical', __name__)
# 簡轉繁 器
s2twp = OpenCC('s2twp')
# 繁轉簡 器
tw2sp = OpenCC('tw2sp')


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


@lexical_blueprint.route('/lexical/sentences', methods=['POST'])
@authenticate
def analyze(resp, login_type):
    # get post data
    post_data = request.get_json()

    print(f'post_data={post_data}, dataType={type(post_data)}', file=sys.stderr)

    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400

    sentences = post_data.get('sentences')
    print(f'sentence={sentences}, dataType={type(sentences)}', file=sys.stderr)

    if not isinstance(sentences, list):
        return jsonify(response_object), 400

    # 客製化的分類詞性
    # reference: https://gist.github.com/hscspring/c985355e0814f01437eaf8fd55fd7998
    nounFlags = ["n","nr","nrfg","nrt","ns","nt","nz"]
    verbFlags = ["v","vd","vi","vn","vq"]
    adjFlags = ["a","ad","an"]

    nouns = {}
    verbs = {}
    adjs = {}

    # 分詞，並依照詞性填入對應的dict 中
    for sentence in sentences:
        print(f'sentence={sentence}, dataType={type(sentence)}', file=sys.stderr)

        if sentence is None:
            continue

        sentence = tw2sp.convert(sentence)
        words = pseg.cut(sentence)

        for word, flag in words:
            if flag in nounFlags:
                nouns[s2twp.convert(word)] = nouns.get(s2twp.convert(word), 0) + 1
            elif flag in verbFlags:
                verbs[s2twp.convert(word)] = verbs.get(s2twp.convert(word), 0) + 1
            elif flag in adjFlags:
                adjs[s2twp.convert(word)] = adjs.get(s2twp.convert(word), 0) + 1
            print(f'{word} {flag}', file=sys.stderr)

    result = {}
    result["nouns"] = nouns
    result["verbs"] = verbs
    result["adjs"] = adjs

    # If ensure_ascii is false,
    # then the return value will be a unicode instance subject to normal Python str
    # to unicode coercion rules instead of being escaped to an ASCII str.
    return jsonify({
        'status': 'success',
        'message': json.dumps(result, ensure_ascii=False)
    })
