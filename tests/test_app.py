import os
import sys

# Ensure the project root is in sys.path so "app" can be imported.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from jinja2 import DictLoader
from sqlalchemy import inspect
from app import app, db, Signup, create_tables, main

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Override templates with simple strings for test assertions.
    app.jinja_loader = DictLoader({
        "signup.html": "{{ message }}",
        "login.html": "{{ message }}",
        "admin.html": "{% for signup in signups %}{{ signup.email }} {% endfor %}",
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_signup_get(client):
    response = client.get('/')
    assert response.status_code == 200
    # GET request should render with an empty message.
    assert b"" in response.data

def test_signup_post_success(client):
    data = {'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com'}
    response = client.post('/', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Successfully signed up!" in response.data

def test_signup_post_duplicate(client):
    data = {'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com'}
    # First signup should succeed.
    response1 = client.post('/', data=data, follow_redirects=True)
    assert b"Successfully signed up!" in response1.data
    # A duplicate signup triggers an IntegrityError.
    response2 = client.post('/', data=data, follow_redirects=True)
    assert b"Error: This email is already registered." in response2.data

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_login_post_valid(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    with client.session_transaction() as sess:
        assert sess.get('admin') is True
    assert response.status_code == 200

def test_login_post_invalid(client):
    response = client.post('/login', data={'username': 'user', 'password': 'wrong'}, follow_redirects=True)
    assert b"Invalid credentials" in response.data

def test_admin_without_login(client):
    response = client.get('/admin', follow_redirects=True)
    # Should redirect to /login when not logged in.
    assert response.request.path == '/login'

def test_admin_with_login(client):
    # Log in as admin.
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    # Insert a signup record to display.
    with app.app_context():
        signup = Signup(first_name="Bob", last_name="Brown", email="bob@example.com")
        db.session.add(signup)
        db.session.commit()
    response = client.get('/admin')
    assert response.status_code == 200
    assert b"bob@example.com" in response.data

def test_logout(client):
    # Log in to set session.
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    with client.session_transaction() as sess:
        assert sess.get('admin') is True
    response = client.get('/logout', follow_redirects=True)
    with client.session_transaction() as sess:
        assert sess.get('admin') is None
    assert response.request.path == '/login'

def test_create_tables(client):
    # Drop all tables, then manually call create_tables().
    with app.app_context():
        db.drop_all()
        create_tables()
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        assert 'signup' in table_names

# --- New Tests to Cover Missing Lines ---

def test_signup_repr():
    # Create a Signup instance and check its __repr__ output.
    signup = Signup(first_name="Test", last_name="User", email="test@example.com")
    assert repr(signup) == "<Signup test@example.com>"

def test_main(monkeypatch):
    # Monkeypatch app.run so we don't actually start the server.
    called = False
    def fake_run(*args, **kwargs):
        nonlocal called
        called = True
    monkeypatch.setattr(app, "run", fake_run)
    main()
    assert called

def test_main_if_block(monkeypatch):
    import runpy
    import werkzeug.serving
    # Monkeypatch werkzeug.serving.run_simple so the server doesn't start.
    monkeypatch.setattr(werkzeug.serving, "run_simple", lambda *args, **kwargs: None)
    runpy.run_path(
        os.path.join(os.path.dirname(__file__), "..", "app.py"),
        run_name="__main__"
    )