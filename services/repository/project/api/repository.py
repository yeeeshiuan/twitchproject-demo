# project/api/repository.py

import sys

from flask import Blueprint, jsonify, json, request

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

    name = "normal_"
    if resp["data"]["twitch_id"]:
        name = "twitch_" + resp["data"]["twitch_id"]
    elif resp["data"]["google_id"]:
        name = "google_" + resp["data"]["google_id"]
    else:
        name = name + resp["data"]["id"]

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


@repository_blueprint.route('/repository/insertone', methods=['POST'])
@authenticate
def insert_one(resp, login_type):

    name = "normal_"
    if resp["data"]["twitch_id"]:
        name = "twitch_" + resp["data"]["twitch_id"]
    elif resp["data"]["google_id"]:
        name = "google_" + resp["data"]["google_id"]
    else:
        name = name + resp["data"]["id"]

    userClient = MongoClient(f"mongodb://{name}:{name}@mongo-db:27017/{name}")
    db = userClient[name]
    asdfCollection = db["asdf"]

    try:
        resAsdf = asdfCollection.insert_one({"_id": "9527", 
                                             "name": "test"})
        userClient.close()
    except errors.DuplicateKeyError:
        userClient.close()
        return jsonify({
            'status': 'fail',
            'message': f'Data already exists'
        })

    print(resAsdf, file=sys.stderr) # output <pymongo.results.InsertOneResult object at 0x7f7d717b7f08>
    print(type(resAsdf), file=sys.stderr) # output <class 'pymongo.results.InsertOneResult'>

    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@repository_blueprint.route('/repository/findone', methods=['POST'])
@authenticate
def find_one(resp, login_type):

    name = None
    if resp["data"]["twitch_id"]:
        name = "twitch_" + resp["data"]["twitch_id"]
    elif resp["data"]["google_id"]:
        name = "google_" + resp["data"]["google_id"]
    else:
        name = "normal_" + resp["data"]["id"]

    if not name:
        return jsonify({
            'status': 'Fail',
            'message': 'Internal server error'
        })


    userClient = MongoClient(f"mongodb://{name}:{name}@mongo-db:27017/{name}")
    db = userClient[name]
    asdfCollection = db["asdf"]

    esAsdf = asdfCollection.find_one({"_id": "9527"})
    userClient.close()

    if esAsdf:
        return jsonify({
            'status': 'success',
            'message': 'find',
            'data': esAsdf
        })

    return jsonify({
        'status': 'fail',
        'message': 'Noe find'
    })

@repository_blueprint.route('/repository/update', methods=['POST'])
@authenticate
def update(resp, login_type):

    name = None
    if resp["data"]["twitch_id"]:
        name = "twitch_" + resp["data"]["twitch_id"]
    elif resp["data"]["google_id"]:
        name = "google_" + resp["data"]["google_id"]
    else:
        name = "normal_" + resp["data"]["id"]

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

    userClient = MongoClient(f"mongodb://{name}:{name}@mongo-db:27017/{name}")
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

        messageKeyId = None
        cursor = messagesCollection.find_one({"message":sentenceObj["message"]})
        if cursor:
            messageKeyId = cursor["_id"]
        else:
            cursor = messagesCollection.insert_one({"room_id": sentenceObj["room_id"],
                                                    "tmi_sent_ts": sentenceObj["tmi_sent_ts"], 
                                                    "message": sentenceObj["message"]})
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

    
    userClient.close()
    return jsonify({
        'status': 'success',
        'message': 'Repository update',
    })






