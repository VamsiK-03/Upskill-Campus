import sqlite3
import string
import random
from flask import Flask, render_template, request, redirect

# Initialize Flask application
app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('url_shortener.db', check_same_thread=False)
conn.execute("PRAGMA foreign_keys = 1")  # Enable foreign key support
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS urls (
             id INTEGER PRIMARY KEY,
             long_url TEXT,
             short_code TEXT UNIQUE
             )''')
conn.commit()

# Function to generate a unique short code
def generate_short_code():
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(6))
        c.execute("SELECT COUNT(*) FROM urls WHERE short_code=?", (short_code,))
        result = c.fetchone()
        if result[0] == 0:
            return short_code

# Function to insert a new URL into the database
def insert_url(long_url):
    short_code = generate_short_code()
    c.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
    conn.commit()
    return short_code

# Function to retrieve the long URL from the short code
def get_long_url(short_code):
    c.execute("SELECT long_url FROM urls WHERE short_code=?", (short_code,))
    result = c.fetchone()
    if result:
        return result[0]
    return None

# Route to handle the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle shortening URLs
@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form['long_url']
    short_code = insert_url(long_url)
    short_url = request.host + '/' + short_code
    return render_template('shorten.html', short_url=short_url)

# Route to handle redirection
@app.route('/<short_code>')
def redirect_to_url(short_code):
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    else:
        return "URL not found."

if __name__ == '__main__':
    app.run(debug=True)
