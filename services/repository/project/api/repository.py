# project/api/repository.py

import sys

from flask import Blueprint, jsonify, request, current_app

from project.api.utils import authenticate
from project import mongo
from pymongo import MongoClient, errors


repository_blueprint = Blueprint('repository', __name__)


@repository_blueprint.route('/repository/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@repository_blueprint.route('/repository/authping', methods=['GET'])
@authenticate
def ping_authpong(resp, login_type):
    return jsonify({
        'status': 'success',
        'message': 'pong!',
        'user': resp
    })


@repository_blueprint.route('/repository/createuser', methods=['POST'])
@authenticate
def create_user(resp, login_type):

    name = getDBname(resp)
    if not name:
        return jsonify({
            'status': 'Fail',
            'message': 'Internal server error'
        })

    # logging
    print(f'Create a New user, user name is {name}.',
          file=sys.stderr)
    try:
        # create the db and create the user
        userdb = mongo.cx[name]
        userdb.command("createUser",
                       name,
                       pwd=name,
                       roles=[{"role": "readWrite",
                               "db": name}])

    except errors.DuplicateKeyError:
        return jsonify({
            'status': 'fail',
            'message': f'User {name}@{name} already exists'
        })

    return jsonify({
        'status': 'success',
        'message': f'Register {name}'
    })


@repository_blueprint.route('/repository/update', methods=['POST'])
@authenticate
def update(resp, login_type):

    name = getDBname(resp)
    if not name:
        return jsonify({
            'status': 'Fail',
            'message': 'Internal server error'
        })

    # logging
    print(f'User\'s mongo document({name}) try to update.',
          file=sys.stderr)

    # get post data
    post_data = request.get_json()

    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }

    if not post_data:
        return jsonify(response_object), 400

    sentencesObj = post_data.get('sentencesObj')
    # lgging
    print(f'sentence={sentencesObj}, dataType={type(sentencesObj)}',
          file=sys.stderr)

    if not isinstance(sentencesObj, list):
        return jsonify(response_object), 400

    repository_uri = current_app.config['REPOSITORY_URI']

    if current_app.config['TESTING']:
        db = mongo.cx[name]
    else:
        userClient = MongoClient(f"mongodb://{name}:{name}@" +
                                 repository_uri +
                                 f"/{name}")
        db = userClient[name]

    usersColl = db["users"]
    messagesColl = db["messages"]
    keywordsColl = db["keywords"]

    for sObj in sentencesObj:
        userKey = {"_id": sObj["user_id"]}

        usersColl.update_one(userKey,
                             {"$set": {"username": sObj["username"],
                                       "badges": sObj["badges"],
                                       "display_name": sObj["display_name"]}},
                             upsert=True)
        usersColl.update_one(userKey,
                             {"$push": {"tmi_sent_ts": sObj["tmi_sent_ts"],
                                        "room_id": sObj["room_id"]}})

        messageKeyId = None
        cursor = messagesColl.find_one({"message": sObj["message"]})
        if cursor:
            messageKeyId = cursor["_id"]
        else:
            cursor = messagesColl.insert_one({"message": sObj["message"]})
            messageKeyId = cursor.inserted_id

        usersColl.update_one(userKey,
                             {"$addToSet": {"message_ids": messageKeyId}})

        messagesColl.update_one({"_id": messageKeyId},
                                {"$addToSet": {"user_ids": userKey["_id"]}})

        for k in sObj["keywords"]:
            keywordKeyId = None
            cursor = keywordsColl.find_one({"keyword": k["keyword"]})
            if cursor:
                keywordKeyId = cursor["_id"]
            else:
                tempDict = {}
                tempDict["keyword"] = k["keyword"]
                tempDict["keyword_type"] = k["keyword_type"]
                cursor = keywordsColl.insert_one(tempDict)
                keywordKeyId = cursor.inserted_id

            tempDictK = {}
            tempDictK["user_ids"] = userKey["_id"]
            tempDictK["messages_ids"] = messageKeyId
            keywordsColl.update_one({"_id": keywordKeyId},
                                    {"$addToSet": tempDictK})

            tempDictM = {}
            tempDictM["keyword_ids"] = keywordKeyId
            messagesColl.update_one({"_id": messageKeyId},
                                    {"$addToSet": tempDictM})

    if not current_app.config['TESTING']:
        userClient.close()

    return jsonify({
        'status': 'success',
        'message': 'Repository update',
    })


@repository_blueprint.route('/repository/findSentencesByUsername/<username>',
                            methods=['GET'])
@authenticate
def findSentencesByUsername(resp, login_type, username):

    name = getDBname(resp)
    if not name:
        return jsonify({
            'status': 'Fail',
            'message': 'Internal server error'
        }), 400

    repository_uri = current_app.config['REPOSITORY_URI']

    if current_app.config['TESTING']:
        db = mongo.cx[name]
    else:
        userClient = MongoClient(f"mongodb://{name}:{name}@" +
                                 repository_uri +
                                 f"/{name}")
        db = userClient[name]

    # logging
    print(f'Finding sentences by Twitch\'s username({username}),' +
          f' user\'s mongo document is {name}.',
          file=sys.stderr)

    usersColl = db["users"]
    messagesColl = db["messages"]

    userObj = usersColl.find_one({"username": username})

    if not userObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no username, who is {username}.',
        }), 404

    message_ids = userObj["message_ids"]

    messagesObj = []
    for index, message_id in enumerate(message_ids):
        messageObj = {}
        message = messagesColl.find_one({"_id": message_id})
        messageObj["message"] = message["message"]
        messageObj["room_id"] = userObj["room_id"]
        messageObj["tmi_sent_ts"] = userObj["tmi_sent_ts"][index]
        messageObj["id"] = index
        messagesObj.append(messageObj)

    if not current_app.config['TESTING']:
        userClient.close()

    if not messagesObj:
        return jsonify({
            'status': 'Fail',
            'message': 'There is no message.',
        }), 404
    else:
        return jsonify({
            'status': 'success',
            'message': messagesObj,
        })


@repository_blueprint.route('/repository/findSentencesByDisplayname/' +
                            '<display_name>', methods=['GET'])
@authenticate
def findSentencesByDisplayname(resp, login_type, display_name):

    name = getDBname(resp)
    if not name:
        return jsonify({
            'status': 'Fail',
            'message': 'Internal server error'
        }), 400

    repository_uri = current_app.config['REPOSITORY_URI']

    if current_app.config['TESTING']:
        db = mongo.cx[name]
    else:
        userClient = MongoClient(f"mongodb://{name}:{name}@" +
                                 repository_uri +
                                 f"/{name}")
        db = userClient[name]

    # logging
    print(f'Finding sentences by Twitch\'s display name({display_name}),' +
          f' user\'s mongo document is {name}.',
          file=sys.stderr)

    usersColl = db["users"]
    messagesColl = db["messages"]

    userObj = usersColl.find_one({"display_name": display_name})

    if not userObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no display name, who is {display_name}.',
        }), 404

    message_ids = userObj["message_ids"]

    messagesObj = []
    for index, message_id in enumerate(message_ids):
        messageObj = {}
        message = messagesColl.find_one({"_id": message_id})
        messageObj["message"] = message["message"]
        messageObj["room_id"] = userObj["room_id"]
        messageObj["tmi_sent_ts"] = userObj["tmi_sent_ts"][index]
        messageObj["id"] = index
        messagesObj.append(messageObj)

    if not current_app.config['TESTING']:
        userClient.close()

    if not messagesObj:
        return jsonify({
            'status': 'Fail',
            'message': 'There is no message.',
        }), 404
    else:
        return jsonify({
            'status': 'success',
            'message': messagesObj,
        })


@repository_blueprint.route('/repository/findDisplaynamesByKeyword/' +
                            '<keyword>', methods=['GET'])
@authenticate
def findDisplaynamesByKeyword(resp, login_type, keyword):

    name = getDBname(resp)
    if not name:
        return jsonify({
            'status': 'Fail',
            'message': 'Internal server error'
        }), 400

    repository_uri = current_app.config['REPOSITORY_URI']

    if current_app.config['TESTING']:
        db = mongo.cx[name]
    else:
        userClient = MongoClient(f"mongodb://{name}:{name}@" +
                                 repository_uri +
                                 f"/{name}")
        db = userClient[name]

    # logging
    print(f'Finding display name by keyword({keyword}),' +
          f' user\'s mongo document is {name}.',
          file=sys.stderr)

    usersColl = db["users"]
    keywordsColl = db["keywords"]

    keywordObj = keywordsColl.find_one({"keyword": keyword})

    if not keywordObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no keyword({keyword}).',
        }), 404

    user_ids = keywordObj["user_ids"]

    users = []
    for index, user_id in enumerate(user_ids):
        userObj = {}
        user = usersColl.find_one({"_id": user_id})
        userObj["display_name"] = user["display_name"]
        userObj["id"] = index
        users.append(userObj)

    if not current_app.config['TESTING']:
        userClient.close()

    if not users:
        return jsonify({
            'status': 'Fail',
            'message': 'There is no user.',
        }), 404
    else:
        return jsonify({
            'status': 'success',
            'message': users,
        })


@repository_blueprint.route('/repository/findDisplaynamesBySentence/' +
                            '<sentence>', methods=['GET'])
@authenticate
def findDisplaynamesBySentence(resp, login_type, sentence):

    name = getDBname(resp)
    if not name:
        return jsonify({
            'status': 'Fail',
            'message': 'Internal server error'
        }), 400

    repository_uri = current_app.config['REPOSITORY_URI']

    if current_app.config['TESTING']:
        db = mongo.cx[name]
    else:
        userClient = MongoClient(f"mongodb://{name}:{name}@" +
                                 repository_uri +
                                 f"/{name}")
        db = userClient[name]

    # logging
    print(f'Finding display name by sentence({sentence}),' +
          f' user\'s mongo document is {name}.',
          file=sys.stderr)

    usersColl = db["users"]
    messagesColl = db["messages"]
    sObj = messagesColl.find_one({"message": sentence})

    if not sObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no sentence({sentence}).',
        }), 404

    user_ids = sObj["user_ids"]

    users = []
    for index, user_id in enumerate(user_ids):
        userObj = {}
        user = usersColl.find_one({"_id": user_id})
        userObj["display_name"] = user["display_name"]
        userObj["id"] = index
        users.append(userObj)

    if not current_app.config['TESTING']:
        userClient.close()

    if not users:
        return jsonify({
            'status': 'Fail',
            'message': 'There is no user.',
        }), 404
    else:
        return jsonify({
            'status': 'success',
            'message': users,
        })


def getDBname(resp):
    name = None
    if resp["data"]["twitch_id"]:
        name = "twitch_" + resp["data"]["twitch_id"]
    elif resp["data"]["google_id"]:
        name = "google_" + resp["data"]["google_id"]
    elif resp["data"]["id"]:
        name = "normal_" + resp["data"]["id"]
    return name
