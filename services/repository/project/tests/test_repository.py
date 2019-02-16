import json
from mockupdb import go

from project.tests.base import BaseTestCase


class TestRepositoryBlueprint(BaseTestCase):

    def test_ping(self):
        """Ensure the /repository/ping route behaves correctly."""
        response = self.client.get('/repository/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_auth_ping(self):
        """Ensure the /repository/authping route behaves correctly."""
        response = self.client.get(
            '/repository/authping',
            headers=dict(Authorization='Bearer valid', LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_auth_ping_no_token(self):
        """Ensure error is thrown if 'Authorization' header is empty."""
        response = self.client.get(
            '/repository/authping',
            headers=dict(LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertIn('Provide a valid auth token.', data['message'])
        self.assertIn('error', data['status'])

    def test_auth_ping_no_login_type(self):
        """Ensure error is thrown if 'LoginType' header is empty."""
        response = self.client.get(
            '/repository/authping',
            headers=dict(Authorization='Bearer valid')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertIn('There is no login type.', data['message'])
        self.assertIn('error', data['status'])

    def test_auth_ping_invalid_token(self):
        """Ensure error is thrown if 'Authorization' header is invalid."""
        response = self.client.get(
            '/repository/authping',
            headers=dict(Authorization='Bearer invalid', LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token.', data['message'])
        self.assertIn('error', data['status'])

    def test_createuser(self):
        """Ensure the /repository/createuser route behaves correctly."""
        # arrange
        future = go(self.client.post,
                    '/repository/createuser',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )
        request = self.server.receives()
        request.ok()
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertIn('Register twitch_1234567', data['message'])
        self.assertIn('success', data['status'])

    def test_createuser_duplicateKey(self):
        """Ensure error is thrown if the user is already exist."""
        # arrange
        future = go(self.client.post,
                    '/repository/createuser',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )
        self.server.receives().command_err(11000, 'duplicateKey error')
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertIn('User twitch_1234567@twitch_1234567 already exists',
                      data['message'])
        self.assertIn('fail', data['status'])

    def test_createuser_invalid_token(self):
        """Ensure error is thrown if 'Authorization' header is empty."""
        response = self.client.post(
            '/repository/createuser',
            headers=dict(Authorization='Bearer invalid', LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token.', data['message'])
        self.assertIn('error', data['status'])

    def test_findSentencesByUsername(self):
        """Ensure the route behaves correctly."""
        """ /repository/findSentencesByUsername/<username> """
        # arrange
        username = "testUser"
        future = go(self.client.post,
                    f'/repository/findSentencesByUsername/{username}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': 248441332,
                           'firstBatch': [{
                               'id': 248441332,
                               'badges': None,
                               'display_name': username,
                               'username': username,
                               'room_id': ['24765850'],
                               'tmi_sent_ts': ['1549100925855'],
                               'message_ids': ['5c5556beb73882000e44a6a3']}]})

        request = self.server.receives()
        request.ok(cursor={'id': '5c5556beb73882000e44a6a3',
                           'firstBatch': [{
                               'id': '5c5556beb73882000e44a6a3',
                               'message': '???'}]})

        message = []
        messageObj = {}
        messageObj["message"] = "???"
        messageObj["room_id"] = ["24765850"]
        messageObj["tmi_sent_ts"] = "1549100925855"
        messageObj["id"] = 0
        message.append(messageObj)

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertEqual(message, data['message'])
        self.assertIn('success', data['status'])

    def test_findSentencesByUsername_username_not_found(self):
        """Ensure error is thrown if the username is not exist."""
        # arrange
        username = "testUser"
        future = go(self.client.post,
                    f'/repository/findSentencesByUsername/{username}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': None, 'firstBatch': []})
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual(f'There is no username, who is {username}.',
                         data['message'])
        self.assertIn('Fail', data['status'])

    def test_findSentencesByUsername_no_message(self):
        """Ensure error is thrown if no message exist."""
        # arrange
        username = "testUser"
        future = go(self.client.post,
                    f'/repository/findSentencesByUsername/{username}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': 248441332,
                           'firstBatch': [{
                               'id': 248441332,
                               'badges': None,
                               'display_name': username,
                               'username': username,
                               'room_id': [],
                               'tmi_sent_ts': [],
                               'message_ids': []}]})
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual('There is no message.', data['message'])
        self.assertIn('Fail', data['status'])

    def test_findSentencesByDisplayname(self):
        """Ensure the route behaves correctly."""
        """ /repository/findSentencesByDisplayname/<display_name> """
        # arrange
        display_name = "testUser"
        future = go(self.client.post,
                    f'/repository/findSentencesByDisplayname/{display_name}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': 248441332,
                           'firstBatch': [{
                               'id': 248441332,
                               'badges': None,
                               'display_name': display_name,
                               'username': display_name,
                               'room_id': ['24765850'],
                               'tmi_sent_ts': ['1549100925855'],
                               'message_ids': ['5c5556beb73882000e44a6a3']}]})

        request = self.server.receives()
        request.ok(cursor={'id': '5c5556beb73882000e44a6a3',
                           'firstBatch': [{'id': '5c5556beb73882000e44a6a3',
                                           'message': '???'}]})

        message = []
        messageObj = {}
        messageObj["message"] = "???"
        messageObj["room_id"] = ["24765850"]
        messageObj["tmi_sent_ts"] = "1549100925855"
        messageObj["id"] = 0
        message.append(messageObj)

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertEqual(message, data['message'])
        self.assertIn('success', data['status'])

    def test_findSentencesByDisplayname_displayname_not_found(self):
        """Ensure error is thrown if the displayname is not exist."""
        # arrange
        display_name = "testUser"
        future = go(self.client.post,
                    f'/repository/findSentencesByDisplayname/{display_name}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': None, 'firstBatch': []})
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual(f'There is no display name, who is {display_name}.',
                         data['message'])
        self.assertIn('Fail', data['status'])

    def test_findSentencesByDisplayname_no_message(self):
        """Ensure error is thrown if no message exist."""
        # arrange
        display_name = "testUser"
        future = go(self.client.post,
                    f'/repository/findSentencesByDisplayname/{display_name}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': 248441332,
                           'firstBatch': [{
                               'id': 248441332,
                               'badges': None,
                               'display_name': display_name,
                               'username': display_name,
                               'room_id': [],
                               'tmi_sent_ts': [],
                               'message_ids': []}]})
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual('There is no message.', data['message'])
        self.assertIn('Fail', data['status'])

    def test_findDisplaynamesByKeyword(self):
        """Ensure the route behaves correctly."""
        """ /repository/findDisplaynamesByKeyword/<keyword> """
        # arrange
        keyword = "noun"
        future = go(self.client.post,
                    f'/repository/findDisplaynamesByKeyword/{keyword}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               'id': '5c555871b73882000e44a89a',
                               'keyword': keyword,
                               'keyword_type': 'n',
                               'user_ids': ['1549100925855'],
                               'message_ids': ['5c5556beb73882000e44a6a3']}]})

        request = self.server.receives()
        request.ok(cursor={'id': '1549100925855',
                           'firstBatch': [{'id': '1549100925855',
                                           'display_name': 'test9527'}]})

        users = []
        userObj = {}
        userObj["display_name"] = "test9527"
        userObj["id"] = 0
        users.append(userObj)

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertEqual(users, data['message'])
        self.assertIn('success', data['status'])

    def test_findDisplaynamesByKeyword_keyword_not_found(self):
        """Ensure error is thrown if the keyword is not exist."""
        # arrange
        keyword = "noun"
        future = go(self.client.post,
                    f'/repository/findDisplaynamesByKeyword/{keyword}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': None, 'firstBatch': []})

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual(f'There is no keyword({keyword}).', data['message'])
        self.assertIn('Fail', data['status'])

    def test_findDisplaynamesByKeyword_no_user(self):
        """Ensure error is thrown if no user exist."""
        # arrange
        keyword = "noun"
        future = go(self.client.post,
                    f'/repository/findDisplaynamesByKeyword/{keyword}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               'id': '5c555871b73882000e44a89a',
                               'keyword': keyword,
                               'keyword_type': 'n',
                               'user_ids': [],
                               'message_ids': ['5c5556beb73882000e44a6a3']}]})

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual('There is no user.', data['message'])
        self.assertIn('Fail', data['status'])

    def test_findDisplaynamesBySentence(self):
        """Ensure the route behaves correctly."""
        """  /repository/findDisplaynamesBySentence/<sentence> """
        # arrange
        sentence = "abcd"
        future = go(self.client.post,
                    f'/repository/findDisplaynamesBySentence/{sentence}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               'id': '5c555871b73882000e44a89a',
                               'message': sentence,
                               'user_ids': ['1549100925855'],
                               'keyword_ids': ['5c5556beb73882000e44a6a3']}]})

        request = self.server.receives()
        request.ok(cursor={'id': '1549100925855',
                           'firstBatch': [{'display_name': 'test9527',
                                           '_id': '1549100925855'}]})

        users = []
        userObj = {}
        userObj["display_name"] = "test9527"
        userObj["id"] = 0
        users.append(userObj)

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertEqual(users, data['message'])
        self.assertIn('success', data['status'])

    def test_findDisplaynamesBySentence_sentence_not_found(self):
        """Ensure error is thrown if the sentence is not exist."""

        # arrange
        sentence = "abcd"
        future = go(self.client.post,
                    f'/repository/findDisplaynamesBySentence/{sentence}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': None, 'firstBatch': []})

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual(f'There is no sentence({sentence}).', data['message'])
        self.assertIn('Fail', data['status'])

    def test_findDisplaynamesBySentence_no_user(self):
        """Ensure error is thrown if no user exist."""
        # arrange
        sentence = "abcd"
        future = go(self.client.post,
                    f'/repository/findDisplaynamesBySentence/{sentence}',
                    headers=dict(Authorization='Bearer valid', LoginType='sso')
                    )

        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               '_id': '5c555871b73882000e44a89a',
                               'message': sentence,
                               'user_ids': [],
                               'keyword_ids': ['5c5556beb73882000e44a6a3']}]})

        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 404)
        self.assertEqual('There is no user.', data['message'])
        self.assertIn('Fail', data['status'])

    def test_update(self):
        """Ensure the /repository/update route behaves correctly."""
        # arrange
        data = {}

        keywords = []
        keyword = {}
        keyword['keyword'] = "noun"
        keyword['keyword_type'] = "n"
        keywords.append(keyword)

        sentencesObj = []
        sentenceObj = {}
        sentenceObj['badges'] = 'vip/1'
        sentenceObj['display_name'] = '黑川大輝'
        sentenceObj['username'] = 'joey777'
        sentenceObj['user_id'] = '95272'
        sentenceObj['room_id'] = '1234'
        sentenceObj['tmi_sent_ts'] = '1234567899'
        sentenceObj['message'] = 'noun'
        sentenceObj['keywords'] = keywords
        sentencesObj.append(sentenceObj)

        data['sentencesObj'] = sentencesObj

        future = go(self.client.post,
                    '/repository/update',
                    headers=dict(Authorization='Bearer valid',
                                 LoginType='sso'),
                    data=json.dumps(data),
                    content_type='application/json'
                    )

        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               '_id': '5c555871b73882000e44a89a'}]})
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               '_id': '5c555871b73882000e44a89a'}]})
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok()
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertEqual("Repository update", data['message'])
        self.assertIn('success', data['status'])

    def test_update_first_time(self):
        """Ensure the /repository/update route behaves correctly."""
        # arrange
        data = {}

        keywords = []
        keyword = {}
        keyword['keyword'] = "noun"
        keyword['keyword_type'] = "n"
        keywords.append(keyword)

        sentencesObj = []
        sentenceObj = {}
        sentenceObj['badges'] = 'vip/1'
        sentenceObj['display_name'] = '黑川大輝'
        sentenceObj['username'] = 'joey777'
        sentenceObj['user_id'] = '95272'
        sentenceObj['room_id'] = '1234'
        sentenceObj['tmi_sent_ts'] = '1234567899'
        sentenceObj['message'] = 'noun'
        sentenceObj['keywords'] = keywords
        sentencesObj.append(sentenceObj)

        data['sentencesObj'] = sentencesObj

        future = go(self.client.post,
                    '/repository/update',
                    headers=dict(Authorization='Bearer valid',
                                 LoginType='sso'),
                    data=json.dumps(data),
                    content_type='application/json'
                    )

        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok(cursor={'id': None, 'firstBatch': []})
        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               '_id': '5c555871b73882000e44a89a'}]})
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok(cursor={'id': None, 'firstBatch': []})
        request = self.server.receives()
        request.ok(cursor={'id': '5c555871b73882000e44a89a',
                           'firstBatch': [{
                               '_id': '5c555871b73882000e44a89a'}]})
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok()
        # act
        http_response = future()
        # assert
        data = json.loads(http_response.data.decode())
        self.assertEqual(http_response.status_code, 200)
        self.assertEqual("Repository update", data['message'])
        self.assertIn('success', data['status'])

    def test_update_no_json_data(self):
        """Ensure error is thrown if no json data."""
        response = self.client.post(
            '/repository/update',
            headers=dict(Authorization='Bearer valid', LoginType='sso')
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('fail', data['status'])

    def test_update_invalid_json_data(self):
        """Ensure error is thrown if no json data."""
        response = self.client.post(
            '/repository/update',
            headers=dict(Authorization='Bearer valid', LoginType='sso'),
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('fail', data['status'])
