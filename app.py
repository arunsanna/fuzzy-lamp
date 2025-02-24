from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Signup model
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return f'<Signup {self.email}>'

# Create tables before first request
@app.before_first_request
def create_tables():
    db.create_all()

# Signup route (displays success message and clears form upon success)
from sqlalchemy.exc import IntegrityError

@app.route('/', methods=['GET', 'POST'])
def signup():
    message = None
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        if first_name and last_name and email:
            new_signup = Signup(first_name=first_name, last_name=last_name, email=email)
            db.session.add(new_signup)
            try:
                db.session.commit()
                message = "Successfully signed up!"
            except IntegrityError:
                db.session.rollback()
                message = "Error: This email is already registered."
    return render_template('signup.html', message=message)

# Admin login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            message = "Invalid credentials"
    return render_template('login.html', message=message)

# Admin page (protected)
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    signups = Signup.query.all()
    return render_template('admin.html', signups=signups)

# Logout route
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))
def main():
    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__':
    main()