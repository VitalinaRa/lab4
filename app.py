from flask import Flask, request, render_template_string, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Підключення до бази з середовища
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cloudlabdb_user:4XkeqLaRXTLOROm4oyZsYy7HnaI60K58@dpg-d0hqtpeuk2gs73888kv0-a.oregon-postgres.render.com/cloudlabdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель таблиці
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

# Створення таблиць один раз
with app.app_context():
    db.create_all()

# HTML-шаблон (інтегрований)
TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Користувачі</title>
    <style>
        body { font-family: sans-serif; padding: 2em; }
        form { margin-bottom: 2em; }
        input { margin: 0.5em; padding: 0.5em; }
        table { border-collapse: collapse; width: 100%; margin-top: 1em; }
        th, td { border: 1px solid #ccc; padding: 0.5em; }
        th { background-color: #f0f0f0; }
    </style>
</head>
<body>
    <h1>Додати користувача</h1>
    <form method="POST" action="/add">
        <input type="text" name="name" placeholder="Ім’я" required>
        <input type="email" name="email" placeholder="Email" required>
        <button type="submit">Додати</button>
    </form>

    <h2>Список користувачів</h2>
    <table>
        <tr><th>ID</th><th>Ім’я</th><th>Email</th></tr>
        {% for user in users %}
        <tr><td>{{ user.id }}</td><td>{{ user.name }}</td><td>{{ user.email }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Головна сторінка
@app.route('/')
def index():
    users = User.query.all()
    return render_template_string(TEMPLATE, users=users)

# Додавання користувача
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    if not User.query.filter_by(email=email).first():
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
    return redirect('/')
    
if __name__ == '__main__':
    app.run(debug=True)
