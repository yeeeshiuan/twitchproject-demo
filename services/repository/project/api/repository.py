# project/api/repository.py

import sys

from flask import Blueprint, jsonify, json, request, current_app

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

    try:
        # create the db and create the user
        userdb = mongo.cx[name]
        result = userdb.command("createUser",
                                 name,
                                 pwd=name,
                                 roles=[{"role":"readWrite", 
                                         "db":name}])

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

    # get post data
    post_data = request.get_json()
    print(f'post_data={post_data}, dataType={type(post_data)}', file=sys.stderr)

    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }

    if not post_data:
        return jsonify(response_object), 400

    sentencesObj = post_data.get('sentencesObj')
    print(f'sentence={sentencesObj}, dataType={type(sentencesObj)}', file=sys.stderr)

    if not isinstance(sentencesObj, list):
        return jsonify(response_object), 400

    repository_uri = current_app.config['REPOSITORY_URI']

    if current_app.config['TESTING']:
        db = mongo.cx[name]
    else:
        userClient = MongoClient(f"mongodb://{name}:{name}@" + repository_uri + f"/{name}")
        db = userClient[name]

    usersCollection = db["users"]
    messagesCollection = db["messages"]
    keywordsCollection = db["keywords"]

    for sentenceObj in sentencesObj:
        userKey = {"_id": sentenceObj["user_id"]}

        usersCollection.update_one(userKey, 
                                   {"$set":{"username": sentenceObj["username"], 
                                            "badges": sentenceObj["badges"], 
                                            "display_name": sentenceObj["display_name"]}}, 
                                   upsert=True)
        usersCollection.update_one(userKey,
                                   {"$push": {"tmi_sent_ts": sentenceObj["tmi_sent_ts"],
                                                  "room_id": sentenceObj["room_id"]}})

        messageKeyId = None
        cursor = messagesCollection.find_one({"message":sentenceObj["message"]})
        if cursor:
            messageKeyId = cursor["_id"]
        else:
            cursor = messagesCollection.insert_one({"message": sentenceObj["message"]})
            messageKeyId = cursor.inserted_id

        usersCollection.update_one(userKey, 
                                   {"$addToSet": {"message_ids": messageKeyId}})

        messagesCollection.update_one({"_id": messageKeyId}, 
                                      {"$addToSet": {"user_ids": userKey["_id"]}})

        for k in sentenceObj["keywords"]:
            keywordKeyId = None
            cursor = keywordsCollection.find_one({"keyword": k["keyword"]})
            if cursor:
                keywordKeyId = cursor["_id"]
            else:
                cursor = keywordsCollection.insert_one({"keyword": k["keyword"], 
                                                        "keyword_type": k["keyword_type"]})
                keywordKeyId = cursor.inserted_id

            keywordsCollection.update_one({"_id": keywordKeyId}, 
                                          {"$addToSet": {"user_ids": userKey["_id"], 
                                                         "messages_ids": messageKeyId}})

            messagesCollection.update_one({"_id": messageKeyId}, 
                                          {"$addToSet": {"keyword_ids": keywordKeyId}})

    if not current_app.config['TESTING']:
        userClient.close()

    return jsonify({
        'status': 'success',
        'message': 'Repository update',
    })


@repository_blueprint.route('/repository/findSentencesByUsername/<username>', methods=['POST'])
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
        userClient = MongoClient(f"mongodb://{name}:{name}@" + repository_uri + f"/{name}")
        db = userClient[name]

    usersCollection = db["users"]
    messagesCollection = db["messages"]

    userObj = usersCollection.find_one({"username": username});

    if not userObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no username, who is {username}.',
        }), 404

    message_ids = userObj["message_ids"]

    messagesObj = []
    for index, message_id in enumerate(message_ids):
        messageObj = {}
        message = messagesCollection.find_one({"_id": message_id})
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


@repository_blueprint.route('/repository/findSentencesByDisplayname/<display_name>', methods=['POST'])
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
        userClient = MongoClient(f"mongodb://{name}:{name}@" + repository_uri + f"/{name}")
        db = userClient[name]

    usersCollection = db["users"]
    messagesCollection = db["messages"]

    userObj = usersCollection.find_one({"display_name": display_name});

    if not userObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no display name, who is {display_name}.',
        }), 404

    message_ids = userObj["message_ids"]

    messagesObj = []
    for index, message_id in enumerate(message_ids):
        messageObj = {}
        message = messagesCollection.find_one({"_id": message_id})
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


@repository_blueprint.route('/repository/findDisplaynamesByKeyword/<keyword>', methods=['POST'])
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
        userClient = MongoClient(f"mongodb://{name}:{name}@" + repository_uri + f"/{name}")
        db = userClient[name]

    usersCollection = db["users"]
    keywordsCollection = db["keywords"]

    keywordObj = keywordsCollection.find_one({"keyword": keyword});

    if not keywordObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no keyword({keyword}).',
        }), 404

    user_ids = keywordObj["user_ids"]

    users = []
    for index, user_id in enumerate(user_ids):
        userObj = {}
        user = usersCollection.find_one({"_id": user_id})
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


@repository_blueprint.route('/repository/findDisplaynamesBySentence/<sentence>', methods=['POST'])
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
        userClient = MongoClient(f"mongodb://{name}:{name}@" + repository_uri + f"/{name}")
        db = userClient[name]

    usersCollection = db["users"]
    messagesCollection = db["messages"]
    print(f'sentence={sentence}', file=sys.stderr)
    sentenceObj = messagesCollection.find_one({"message": sentence});

    if not sentenceObj:
        return jsonify({
            'status': 'Fail',
            'message': f'There is no sentence({sentence}).',
        }), 404

    user_ids = sentenceObj["user_ids"]

    users = []
    for index, user_id in enumerate(user_ids):
        userObj = {}
        user = usersCollection.find_one({"_id": user_id})
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

