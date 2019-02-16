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
    # https://gist.github.com/hscspring/c985355e0814f01437eaf8fd55fd7998
    nounFlags = ["n", "nr", "nrfg", "nrt", "ns", "nt", "nz"]
    verbFlags = ["v", "vd", "vi", "vn", "vq"]
    adjFlags = ["a", "ad", "an"]

    nouns = {}
    verbs = {}
    adjs = {}

    keywordsBySentence = []

    # 分詞，並依照詞性填入對應的dict 中
    for sentence in sentences:
        print(f'sentence={sentence}, dataType={type(sentence)}',
              file=sys.stderr)

        if sentence is None:
            continue

        sentence = tw2sp.convert(sentence)
        words = pseg.cut(sentence)

        tempArray = []
        keywordsInSentence = []

        for word, flag in words:
            # 一句話裡的字詞只有效一次
            if word in tempArray:
                continue

            if flag in nounFlags:
                tempArray.append(word)
                wordTra = s2twp.convert(word)
                nouns[wordTra] = nouns.get(wordTra, 0) + 1
                keywordsInSentence.append(dict_factory(wordTra, flag))
            elif flag in verbFlags:
                tempArray.append(word)
                wordTra = s2twp.convert(word)
                verbs[wordTra] = verbs.get(wordTra, 0) + 1
                keywordsInSentence.append(dict_factory(wordTra, flag))
            elif flag in adjFlags:
                tempArray.append(word)
                wordTra = s2twp.convert(word)
                adjs[wordTra] = adjs.get(wordTra, 0) + 1
                keywordsInSentence.append(dict_factory(wordTra, flag))

        keywordsBySentence.append(keywordsInSentence)
        print(f'{keywordsInSentence}', file=sys.stderr)

    result = {}
    result["nouns"] = nouns
    result["verbs"] = verbs
    result["adjs"] = adjs

    # If ensure_ascii is false,
    # then the return value will be a unicode instance subject to normal str
    # to unicode coercion rules instead of being escaped to an ASCII str.
    return jsonify({
        'status': 'success',
        'keywords': json.dumps(result, ensure_ascii=False),
        'keywordsBySentence': json.dumps(keywordsBySentence,
                                         ensure_ascii=False)
    })


def dict_factory(keyword, flag):
    temp_dict = {}
    temp_dict["keyword"] = keyword
    temp_dict["keyword_type"] = flag
    return temp_dict
