from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

class UserModelTextCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.uid = 56789
        u = User.signup('test1', 'test1@test.com' 'test_password', None)
        u.id = self.uid
        db.session.commit()

        self.user = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        m = Message(
            text='test text 1',
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u.messages),1)
        self.assertEqual(self.u.messages[0].test, 'test text 1')

    def test_message_likes(self):
        m1 = Message(
            text="test text 2",
            user_id=self.uid
        )

    
        u = User.signup("test2", "test2@test.com", "test_password2", None)
        uid = 12345
        u.id = uid
        db.session.add_all([m1, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)
