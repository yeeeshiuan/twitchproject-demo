# project/tests/base.py


from flask_testing import TestCase
from mockupdb import MockupDB

from project import create_app, mongo

app = create_app("test")


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        self.server = MockupDB(auto_ismaster=True)
        self.server.run()
        app.config['MONGO_URI'] = self.server.uri
        mongo.init_app(app)
        return app

    def setUp(self):
        pass

    def tearDown(self):
        self.server.stop()
