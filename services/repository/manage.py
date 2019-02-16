# manage.py

import unittest
import coverage
import sys

from flask.cli import FlaskGroup
from pymongo import MongoClient, errors
from flask import current_app

from project import create_app, mongo


COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/config.py',
    ]
)
COV.start()

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def create_user():
    """create the database."""
    name='twitch_9527'

    try:
        # create the db and create the user
        userdb = mongo.cx[name]
        result = userdb.command("createUser",
                                 name,
                                 pwd=name,
                                 roles=[{"role":"readWrite", 
                                         "db":name}])
        print(f'DB({name}) added successful.', file=sys.stderr)
    except errors.DuplicateKeyError:
        print(f'DB({name}) already exist.', file=sys.stderr)

@cli.command()
def seed_db():
    """Seeds the database."""
    name='twitch_9527'
    sentencesObj = []
    keywords = []
    keyword = {}
    keyword['keyword'] = "工程師"
    keyword['keyword_type'] = "n"
    keywords.append(keyword)

    sentencesObj = []
    sentenceObj = {}
    sentenceObj['badges'] = 'vip/999'
    sentenceObj['display_name'] = '煞氣的Joey'
    sentenceObj['username'] = 'joey777'
    sentenceObj['user_id'] = '9527'
    sentenceObj['room_id'] = '5987'
    sentenceObj['tmi_sent_ts'] = '1234567890'
    sentenceObj['message'] = '工程師是你？'
    sentenceObj['keywords'] = keywords
    sentencesObj.append(sentenceObj)

    repository_uri = current_app.config['REPOSITORY_URI']

    try:
        if current_app.config['TESTING']:
            db = mongo.cx[name]
        else:
            userClient = MongoClient(f"mongodb://{name}:{name}@" + repository_uri + f"/{name}")
            db = userClient[name]
    except e:
        print(f'Error occur.({e})', file=sys.stderr)

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

    print(f'Data added successful.', file=sys.stderr)

@cli.command()
def test():
    """ Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report(show_missing=True)
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == '__main__':
    cli()
