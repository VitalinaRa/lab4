from flask import Flask, request, render_template_string, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret')  # для flash повідомлень

# Підключення до бази з середовища
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://cloudlabdb_user:4XkeqLaRXTLOROm4oyZsYy7HnaI60K58@dpg-d0hqtpeuk2gs73888kv0-a.oregon-postgres.render.com/cloudlabdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель таблиці
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

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
        .actions { display: flex; gap: 0.5em; }
        .flash { color: green; }
    </style>
</head>
<body>
    <h1>Користувачі</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash">
          {% for msg in messages %}
            <p>{{ msg }}</p>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <!-- Форма для створення/редагування -->
    <h2>{{ 'Редагувати користувача' if edit else 'Додати користувача' }}</h2>
    <form method="POST" action="{{ url_for('save_user') }}">
        <input type="hidden" name="id" value="{{ user.id if user else '' }}">
        <input type="text" name="name" placeholder="Ім’я" value="{{ user.name if user else '' }}" required>
        <input type="email" name="email" placeholder="Email" value="{{ user.email if user else '' }}" required>
        <button type="submit">{{ 'Оновити' if edit else 'Додати' }}</button>
        {% if edit %}<a href="{{ url_for('index') }}">Скасувати</a>{% endif %}
    </form>

    <h2>Список користувачів</h2>
    <table>
        <tr><th>ID</th><th>Ім’я</th><th>Email</th><th>Дії</th></tr>
        {% for u in users %}
        <tr>
            <td>{{ u.id }}</td>
            <td>{{ u.name }}</td>
            <td>{{ u.email }}</td>
            <td class="actions">
                <a href="{{ url_for('edit_user', user_id=u.id) }}">Редагувати</a>
                <a href="{{ url_for('delete_user', user_id=u.id) }}" onclick="return confirm('Видалити користувача?');">Видалити</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Головна сторінка — список та форма
@app.route('/')
def index():
    users = User.query.all()
    return render_template_string(TEMPLATE, users=users, edit=False, user=None)

# Маршрут збереження (створення або оновлення)
@app.route('/save', methods=['POST'])
def save_user():
    user_id = request.form.get('id')
    name = request.form['name']
    email = request.form['email']

    if user_id:
        # Оновлення
        user = User.query.get(user_id)
        if user:
            # Перевірка унікальності email
            existing = User.query.filter(User.email == email, User.id != user_id).first()
            if existing:
                flash('Email вже використовується іншим користувачем.')
                return redirect(url_for('edit_user', user_id=user_id))
            user.name = name
            user.email = email
            db.session.commit()
            flash('Користувача оновлено.')
    else:
        # Створення
        if User.query.filter_by(email=email).first():
            flash('Email вже існує.')
        else:
            new_user = User(name=name, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Користувача додано.')
    return redirect(url_for('index'))

# Форма редагування
@app.route('/edit/<int:user_id>')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    users = User.query.all()
    return render_template_string(TEMPLATE, users=users, edit=True, user=user)

# Видалення користувача
@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Користувача видалено.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)