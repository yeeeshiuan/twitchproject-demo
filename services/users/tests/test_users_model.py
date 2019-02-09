import unittest

from flask import current_app

from project import db
from project.api.models import UserSSO
from tests.base import BaseTestCase
from tests.utils import add_usersso

from sqlalchemy.exc import IntegrityError


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        self.assertTrue(user.id)
        self.assertEqual(user.username, 'justatest')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.active)
        self.assertEqual(user.picture, 'pictureURL')
        self.assertEqual(user.twitch_id, '1234567890')

    def test_add_user_duplicate_email(self):
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        duplicate_user = UserSSO(
            username='justanothertest',
            email='test@test.com',
            picture='pictureURL',
            twitch_id='1234567890',
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_twitch_id(self):
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        duplicate_user = UserSSO(
            username='justanothertest',
            email='testq@testq.com',
            picture='pictureURL',
            twitch_id='1234567890',
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_to_json(self):
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        self.assertTrue(isinstance(user.to_json(), dict))

    def test_encode_auth_token(self):
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertEqual(UserSSO.decode_auth_token(auth_token), user.id)

    def test_invalid_expired_token(self):
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertEqual(UserSSO.decode_auth_token(auth_token), 'Signature expired. Please log in again.')

    def test_invalid_token(self):
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        user = add_usersso('justatest', 'test@test.com', 'pictureURL', '1234567890')
        auth_token = user.encode_auth_token(user.id)
        self.assertEqual(UserSSO.decode_auth_token("invalid"), 'Invalid token. Please log in again.')

if __name__ == '__main__':
    unittest.main()
