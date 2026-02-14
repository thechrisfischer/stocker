import json
import unittest

from application.app import app
from index import db, limiter


class BaseTestConfig(unittest.TestCase):
    default_user = {
        "email": "default@gmail.com",
        "password": "something2",
    }

    def setUp(self):
        app.config.from_object("config.TestingConfig")
        limiter.enabled = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        res = self.app.post(
            "/api/create_user",
            data=json.dumps(self.default_user),
            content_type="application/json",
        )
        self.token = json.loads(res.data.decode("utf-8"))["token"]

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
