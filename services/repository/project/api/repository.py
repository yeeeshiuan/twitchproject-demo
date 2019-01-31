# project/api/repository.py

import sys

from flask import Blueprint, jsonify, json

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
            'message': 'JSON data wrong'
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


