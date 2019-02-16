import unittest
import coverage
import sys

from flask.cli import FlaskGroup
from sqlalchemy import exc, or_

from project import create_app, db
from project.api.models import UserSSO


COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        './test/*',
        'project/config.py',
    ]
)
COV.start()

app = create_app()

cli = FlaskGroup(create_app=create_app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command()
def seed_db():
    """Seeds the database."""
    twitch_id='9527'
    username='joey'
    email='joey@test.io'
    picture='http://joey.picture'
    try:
        # check for existing user
        user = UserSSO.query.filter(
            or_(UserSSO.twitch_id == twitch_id, UserSSO.email == email)).first()

        if not user:
            db.session.add(UserSSO(
                twitch_id=twitch_id,
                username=username,
                email=email,
                picture=picture
            ))
            db.session.commit()
            print(f'User({username}) added successful.', file=sys.stderr)
        else:
            print(f'User({username}) already exist.', file=sys.stderr)
    # handler errors
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        print(f'Error happened.{e}', file=sys.stderr)

@cli.command()
def test():
    """ Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('tests')
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
