import pytest
from flask import Flask
from flask_testing import TestCase
from app import app, get_db_connection

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        return app

    def setUp(self):
        self.db_connection = get_db_connection()
        self.db_cursor = self.db_connection.cursor()
        self.db_cursor.execute('CREATE TABLE users (id SERIAL PRIMARY KEY, first_name VARCHAR(50) NOT NULL, last_name VARCHAR(50) NOT NULL, email VARCHAR(100) NOT NULL UNIQUE)')
        self.db_connection.commit()

    def tearDown(self):
        self.db_cursor.execute('DROP TABLE users')
        self.db_connection.commit()
        self.db_cursor.close()
        self.db_connection.close()

def test_home_page(self):
    response = self.client.get('/')
    self.assert200(response)
    self.assert_template_used('signup.html')

def test_signup(self):
    response = self.client.post('/signup', data=dict(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com'
    ))
    self.assert200(response)
    self.assertIn(b'User saved successfully!', response.data)

def test_admin_page(self):
    self.client.post('/signup', data=dict(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com'
    ))
    response = self.client.get('/admin')
    self.assert200(response)
    self.assert_template_used('admin.html')
    self.assertIn(b'John', response.data)
    self.assertIn(b'Doe', response.data)
    self.assertIn(b'john.doe@example.com', response.data)
