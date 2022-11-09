from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
app.config['WTF_CSRF_ENABLED'] = False

#################################

db.create_all()


class MessageViewTestCase(TestCase):
    def setUp(self):
        """creates all tables in databsse"""
        db.drop_all()
        db.create_all()
        """sets up self"""
        self.client = app.test_client()

        """creating self and three other users to run testson"""
        self.testuser = User.signup(username="testuser", email="test@test.com", password="testuser", image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id
        db.session.commit()

        self.u1 = User.signup("test_user1", "test1@test.com", "passwordshould hash", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        db.session.commit()

        self.u2 = User.signup("test_user2", "test2@test.com", "passwordshould hash", None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        db.session.commit()

        self.u3 = User.signup("test_user3", "test3@test.com", "passwordshould hash", None)
        db.session.commit()

    def tearDown(self):
        """get rid of testv data"""
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def setup_followers(self):
        """setting up follows to test if they are connected in db"""
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)

        f2 = Follows(user_being_followed_id=self.u2_id,user_following_id=self.testuser_id)

        f3 = Follows(user_being_followed_id=self.testuser_id,user_following_id=self.u1_id)

        db.session.add_all([f1, f2, f3])
        db.session.commit()

    def test_user_show_with_follows(self):
        self.setup_followers()
        with self.client as c:
            """hit route to test followers"""
            resp = c.get(f"/users/{self.testuser_id}")
            self.assertEqual(resp.status_code, 200)

            self.assertIn("@test", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            self.assertIn("0", found[0].text)

            self.assertIn("2", found[1].text)

    def test_show_following(self):
        """hit route to test following - return data"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(resp.status_code, 200)

            self.assertIn("@efg", str(resp.data))
            self.assertNotIn("@hij", str(resp.data))
            self.assertNotIn("@testing", str(resp.data))

    def test_show_followers(self):
        """hit route to test followers - return data"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@abc", str(resp.data))
            self.assertNotIn("@efg", str(resp.data))

    def test_unauthorized_following_page_access(self):
        self.setup_followers()
        """hit route to test following"""
        with self.client as c:
        
            resp = c.get(
                f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthorized_followers_page_access(self):
        """hit route to test folling redirects"""
        self.setup_followers()
        with self.client as c:

            resp = c.get(
                f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
