from flask import Flask, request, redirect,url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Модель: Машина
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)        # марка (Kia)
    model = db.Column(db.String(50), nullable=False)        # модель (Seltos)
    year = db.Column(db.Integer, nullable=False)            # год (2019)
    vin = db.Column(db.String(17))                          # VIN
    license_plate = db.Column(db.String(20))                # госномер
    engine = db.Column(db.String(50))                       # двигатель (1.6 петрол)
    transmission = db.Column(db.String(20))                 # коробка (МКПП)
    color = db.Column(db.String(30))                        # цвет
    purchase_date = db.Column(db.Date)                      # дата покупки
    purchase_mileage = db.Column(db.Integer)                # пробег при покупке
    current_mileage = db.Column(db.Integer)                 # текущий пробег

    def __repr__(self):
        return f'<Car {self.brand} {self.model} {self.year}>'

# Модель: Обслуживание
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)               # дата
    mileage = db.Column(db.Integer, nullable=False)         # пробег на момент работы
    service_type = db.Column(db.String(50), nullable=False) # тип (ТО / Ремонт / Замена расходника)
    description = db.Column(db.String(500))                 # что именно делали
    workshop = db.Column(db.String(100))                    # где делал
    cost = db.Column(db.Integer)                            # стоимость в рублях
    next_service_mileage = db.Column(db.Integer)            # следующее ТО по плану (км)

    car = db.relationship('Car', backref='services')

    def __repr__(self):
        return f'<Service {self.date} {self.service_type}>'


@app.route('/services/new', methods=['GET', 'POST'])
def new_service():
    if request.method == 'POST':
        # Получаем данные из формы
        date_str = request.form['date']
        mileage = int(request.form['mileage'])
        service_type = request.form['service_type']
        description = request.form.get('description', '')
        workshop = request.form.get('workshop', '')
        cost = request.form.get('cost')
        next_service_mileage = request.form.get('next_service_mileage')

        # Преобразуем строку даты в объект Date
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Создаём запись
        car = Car.query.first()
        new_record = Service(
            car_id=car.id,
            date=date,
            mileage=mileage,
            service_type=service_type,
            description=description,
            workshop=workshop,
            cost=int(cost) if cost else None,
            next_service_mileage=int(next_service_mileage) if next_service_mileage else None
        )

        db.session.add(new_record)
        db.session.commit()

        # Возвращаем пользователя к списку
        return redirect(url_for('services'))

    # Если GET-запрос — показываем форму
    return '''
    <h1>➕ Добавить запись об обслуживании</h1>
    <p><a href="/services">← К списку</a></p>

    <form method="POST" style="max-width: 500px;">
        <p>
            <label>Дата:<br>
                <input type="date" name="date" required>
            </label>
        </p>
        <p>
            <label>Пробег (км):<br>
                <input type="number" name="mileage" required>
            </label>
        </p>
        <p>
            <label>Тип работы:<br>
                <select name="service_type" required>
                    <option value="ТО">Регламентное ТО</option>
                    <option value="Ремонт">Ремонт</option>
                    <option value="Расходник">Замена расходника</option>
                    <option value="Шиномонтаж">Шиномонтаж</option>
                    <option value="Кузовной">Кузовной</option>
                    <option value="Другое">Другое</option>
                </select>
            </label>
        </p>
        <p>
            <label>Описание (что делали):<br>
                <textarea name="description" rows="3" cols="50"></textarea>
            </label>
        </p>
        <p>
            <label>Сервис:<br>
                <input type="text" name="workshop" size="50">
            </label>
        </p>
        <p>
            <label>Стоимость (₽):<br>
                <input type="number" name="cost">
            </label>
        </p>
        <p>
            <label>Следующее ТО (пробег, км):<br>
                <input type="number" name="next_service_mileage">
            </label>
        </p>
        <p>
            <button type="submit" style="padding: 10px 20px; font-size: 16px;">Сохранить</button>
        </p>
    </form>
    '''


@app.route('/')
def home():
    car = Car.query.first()
    if car is None:
        return '<h1>Машина пока не добавлена</h1>'

    return f'''
    <h1>🚗 Мой автомобиль</h1>
    <img src="/static/inside_car_sunset.jpg" alt="Моя ласточка" style="max-width: 500px; border-radius: 10px;">
    <p><b>Марка:</b> {car.brand}</p>
    <p><b>Модель:</b> {car.model}</p>
    <p><b>Год:</b> {car.year}</p>
    <p><b>Двигатель:</b> {car.engine}</p>
    <p><b>Коробка:</b> {car.transmission}</p>
    <p><b>Цвет:</b> {car.color}</p>
    <p><b>Текущий пробег:</b> {car.current_mileage} км</p>
    <p><a href="/services">📋 Обслуживание</a></p>
'''


@app.route('/services')
def services():
    all_services = Service.query.order_by(Service.date.desc()).all()

    if not all_services:
        return '''
        <h1>📋 Обслуживание</h1>
        <p>Записей пока нет</p>
        <p><a href="/">← На главную</a></p>
        
        <p><a
        href = "/services/new" >➕ Добавить
        запись </a> </p>
        '''
    rows = ''
    for s in all_services:
        rows += f'''
        <tr>
            <td>{s.date}</td>
            <td>{s.mileage} км</td>
            <td>{s.service_type}</td>
            <td>{s.description or '—'}</td>
            <td>{s.workshop or '—'}</td>
            <td>{s.cost or 0} ₽</td>
        </tr>
        '''

    return f'''
    <h1>📋 Обслуживание</h1>
    <p><a href="/">← На главную</a></p>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr style="background: #f0f0f0;">
                <th>Дата</th>
                <th>Пробег</th>
                <th>Тип</th>
                <th>Описание</th>
                <th>Сервис</th>
                <th>Стоимость</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    '''


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

