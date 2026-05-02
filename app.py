from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для записей
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    client_email = db.Column(db.String(100))
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.client_name} - {self.appointment_date}>'

# Декоратор для защиты админ-панели
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Главная страница - форма записи
@app.route('/')
def index():
    return render_template('index.html')

# Обработка формы записи
@app.route('/book', methods=['POST'])
def book():
    try:
        client_name = request.form.get('client_name')
        client_phone = request.form.get('client_phone')
        client_email = request.form.get('client_email')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        service = request.form.get('service')
        comment = request.form.get('comment')

        if not all([client_name, client_phone, appointment_date, appointment_time, service]):
            flash('Пожалуйста, заполните все обязательные поля!', 'error')
            return redirect(url_for('index'))

        # Преобразование даты
        date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()

        new_appointment = Appointment(
            client_name=client_name,
            client_phone=client_phone,
            client_email=client_email,
            appointment_date=date_obj,
            appointment_time=appointment_time,
            service=service,
            comment=comment
        )

        db.session.add(new_appointment)
        db.session.commit()

        flash('Ваша запись успешно создана! Мы свяжемся с вами.', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при создании записи. Попробуйте позже.', 'error')
        return redirect(url_for('index'))

# Страница входа в админ-панель
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Простая проверка (в продакшене используйте хеширование!)
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('login.html')

# Админ-панель - список записей
@app.route('/admin')
@login_required
def admin_dashboard():
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    return render_template('admin.html', appointments=appointments)

# Изменение статуса записи
@app.route('/admin/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    appointment = Appointment.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'cancelled']:
        appointment.status = new_status
        db.session.commit()
        flash('Статус записи обновлен!', 'success')
    
    return redirect(url_for('admin_dashboard'))

# Удаление записи
@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Запись удалена!', 'success')
    return redirect(url_for('admin_dashboard'))

# Выход из админ-панели
@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

# Инициализация БД
def init_db():
    with app.app_context():
        db.create_all()
        print("База данных создана!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)
