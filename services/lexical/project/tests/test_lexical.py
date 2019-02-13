# project/tests/test_eval.py


import json

from project.tests.base import BaseTestCase


class TestLexicalBlueprint(BaseTestCase):

    def test_ping(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get(
            '/lexical/ping',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_auth_ping(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get(
            '/lexical/authping',
            headers=dict(Authorization='Bearer valid',
                         LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_auth_ping_no_header(self):
        """Ensure error is thrown if header is empty."""
        response = self.client.get('/lexical/authping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertIn('Provide a valid auth token.', data['message'])
        self.assertIn('error', data['status'])

    def test_auth_ping_no_authorization(self):
        """Ensure error is thrown if 'Authorization' header is empty."""
        response = self.client.get(
            '/lexical/authping',
            headers=dict(LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertIn('Provide a valid auth token.', data['message'])
        self.assertIn('error', data['status'])

    def test_auth_ping_no_login_type(self):
        """Ensure error is thrown if 'LoginType' header is empty."""
        response = self.client.get(
            '/lexical/authping',
            headers=dict(Authorization='Bearer valid')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertIn('There is no login type.', data['message'])
        self.assertIn('error', data['status'])

    def test_auth_ping_invalid_authorization(self):
        """Ensure error is thrown if 'Authorization' header is empty."""
        response = self.client.get(
            '/lexical/authping',
            headers=dict(Authorization='Bearer invalid', LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token.', data['message'])
        self.assertIn('error', data['status'])

    def test_analyze(self):
        """Ensure the /lexical/sentences route behaves correctly."""
        response = self.client.post(
            '/lexical/sentences',
            headers=dict(Authorization='Bearer valid',
                         LoginType='sso'),
            data=json.dumps({
                'sentences': ['小怪物', '不用刮刀', '大怪物']
            }),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        keywords = json.loads(data['keywords'])
        keywordsBySentence = json.loads(data['keywordsBySentence'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['keywords'])
        self.assertTrue(data['keywordsBySentence'])
        """ 怪物共有出現兩次；刮刀、不用、小、大都各出現一次。(verb, noun, adj) """
        self.assertEqual(keywords['nouns']['怪物'], 2)
        self.assertEqual(keywords['nouns']['刮刀'], 1)
        self.assertEqual(keywords['verbs']['不用'], 1)
        self.assertEqual(keywords['adjs']['小'], 1)
        self.assertEqual(keywords['adjs']['大'], 1)
        """ 第一句有解出兩分詞；第二句有解出兩分詞；第三句有解出兩分詞 """
        self.assertEqual(len(keywordsBySentence[0]), 2)
        self.assertEqual(len(keywordsBySentence[1]), 2)
        self.assertEqual(len(keywordsBySentence[2]), 2)
        self.assertEqual('success', data['status'])

    def test_analyze_invalid_json(self):
        """Ensure the /lexical/sentences route behaves correctly."""
        response = self.client.post(
            '/lexical/sentences',
            headers=dict(Authorization='Bearer valid',
                         LoginType='sso'),
            data=json.dumps({
                'sentences': '小怪物'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual('fail', data['status'])
        self.assertEqual('Invalid payload.', data['message'])

    def test_analyze_null_payload(self):
        """Ensure the /lexical/sentences route behaves correctly."""
        response = self.client.post(
            '/lexical/sentences',
            headers=dict(Authorization='Bearer valid',
                         LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual('fail', data['status'])
        self.assertEqual('Invalid payload.', data['message'])



