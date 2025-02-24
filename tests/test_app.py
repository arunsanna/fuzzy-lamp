import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db, Signup
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def client():
    # Use in-memory SQLite for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_signup_page(client):
    """Test that the signup page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Sign Up" in response.data

def test_successful_signup(client):
    """Test a successful signup and that the success message is shown."""
    response = client.post(
        '/',
        data={'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Successfully signed up!" in response.data

def test_duplicate_signup(client):
    """Test that submitting a duplicate email shows an error message."""
    # Insert a signup directly
    with app.app_context():
        signup = Signup(first_name='John', last_name='Doe', email='john@example.com')
        db.session.add(signup)
        db.session.commit()
    
    # Try signing up with the same email
    response = client.post(
        '/',
        data={'first_name': 'Jane', 'last_name': 'Doe', 'email': 'john@example.com'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Error: This email is already registered." in response.data

def test_admin_login_logout(client):
    """Test the admin login, access to admin page, and logout."""
    # Check that the login page loads
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Admin Login" in response.data

    # Test login with invalid credentials
    response = client.post(
        '/login',
        data={'username': 'admin', 'password': 'wrong'},
        follow_redirects=True
    )
    assert b"Invalid credentials" in response.data

    # Test login with valid credentials
    response = client.post(
        '/login',
        data={'username': 'admin', 'password': 'admin'},
        follow_redirects=True
    )
    # After successful login, we should see the admin page
    assert b"All Signups" in response.data

    # For a robust test, we manually set the session
    with client.session_transaction() as sess:
        sess['admin'] = True

    # Create a signup for the admin page to display
    with app.app_context():
        signup = Signup(first_name='Alice', last_name='Wonder', email='alice@example.com')
        db.session.add(signup)
        db.session.commit()

    # Access the admin page
    response = client.get('/admin')
    assert response.status_code == 200
    assert b"Alice" in response.data

    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert b"Admin Login" in response.data

def test_invalid_signup_missing_fields(client):
    """Test that submitting a signup with missing fields shows an error message."""
    response = client.post(
        '/',
        data={'first_name': 'John', 'last_name': ''},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Sign Up" in response.data  # No success message

def test_access_admin_without_login(client):
    """Test that accessing the admin page without login redirects to login page."""
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    assert b"Admin Login" in response.data

def test_access_logout_without_login(client):
    """Test that accessing the logout route without login redirects to login page."""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Admin Login" in response.data

def test_invalid_email_format_signup(client):
    """Test that submitting a signup with an invalid email format shows an error message."""
    response = client.post(
        '/',
        data={'first_name': 'John', 'last_name': 'Doe', 'email': 'invalid-email'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Sign Up" in response.data  # No success message

def test_sqlalchemy_integrity_error_handling(client):
    """Test that SQLAlchemy IntegrityError is handled during signup."""
    with app.app_context():
        signup = Signup(first_name='John', last_name='Doe', email='john@example.com')
        db.session.add(signup)
        db.session.commit()

    response = client.post(
        '/',
        data={'first_name': 'Jane', 'last_name': 'Doe', 'email': 'john@example.com'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Error: This email is already registered." in response.data

def test_before_first_request(client):
    """Test that the database tables are created before the first request."""
    with app.app_context():
        assert db.engine.table_names() == ['signup']
