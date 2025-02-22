from flask import Flask, request, render_template
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host="db",
        database="user_db",
        user="user",
        password="password"
    )
    return conn

@app.route('/')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def save_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (first_name, last_name, email) VALUES (%s, %s, %s)',
                (first_name, last_name, email))
    conn.commit()
    cur.close()
    conn.close()

    return 'User saved successfully!'

@app.route('/admin')
def admin():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT first_name, last_name, email FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
