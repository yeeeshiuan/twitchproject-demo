import unittest
import json

from flask import current_app

from tests.base import BaseTestCase
from tests.utils import add_usersso


class TestAuthBlueprint(BaseTestCase):

    def test_user_twitch_register(self):
        with self.client:
            response = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_user_twitch_register_already_exist(self):
        add_usersso('test', 'test@test.test', '1234567890', '123456')
        with self.client:
            response = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Already registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_user_twitch_register_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_twitch_register_invalid_json_keys_no_username(self):
        with self.client:
            response = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_twitch_register_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'picture': '1234567890',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_valid_logout(self):
        with self.client:
            # user login by twitch sso
            resp_login = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            # valid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}',
                         'LoginType': 'sso'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout_expired_token(self):
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        with self.client:
            resp_login = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}',
                         'LoginType': 'sso'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout_auth_token(self):
        with self.client:
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': 'Bearer invalid',
                         'LoginType': 'sso'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout_null_login_type(self):
        with self.client:
            resp_login = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'There is no login type.')
            self.assertEqual(response.status_code, 403)

    def test_invalid_logout_wrong_login_type(self):
        with self.client:
            resp_login = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}',
                         'LoginType': 'sos'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Provide a valid login type.')
            self.assertEqual(response.status_code, 403)

    def test_user_status(self):
        with self.client:
            resp_login = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': f'Bearer {token}',
                         'LoginType': 'sso'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['twitch_id'] == '123456')
            self.assertTrue(data['data']['username'] == 'test')
            self.assertTrue(data['data']['email'] == 'test@test.test')
            self.assertTrue(data['data']['active'])
            self.assertTrue(data['data']['picture'] == '1234567890')
            self.assertEqual(response.status_code, 200)

    def test_invalid_status_wrong_auth_token(self):
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer invalid',
                         'LoginType': 'sso'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_invalid_status_null_auth_token(self):
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'LoginType': 'sso'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 403)

    def test_invalid_status_null_login_type(self):
        with self.client:
            resp_login = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'There is no login type.')
            self.assertEqual(response.status_code, 403)

    def test_invalid_status_wrong_login_type(self):
        with self.client:
            resp_login = self.client.post(
                '/auth/twitchRegister',
                data=json.dumps({
                    'twitch_id': '123456',
                    'username': 'test',
                    'email': 'test@test.test',
                    'picture': '1234567890',
                }),
                content_type='application/json'
            )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}',
                         'LoginType': 'sos'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Provide a valid login type.')
            self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()
