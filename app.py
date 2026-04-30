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
# Модель: Заправка
class Fillup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)               # дата заправки
    mileage = db.Column(db.Integer, nullable=False)         # пробег на момент заправки
    liters = db.Column(db.Float, nullable=False)            # литры
    price_per_liter = db.Column(db.Float, nullable=False)   # цена за литр
    total_cost = db.Column(db.Integer, nullable=False)      # общая стоимость
    gas_station = db.Column(db.String(100))                 # АЗС (Лукойл / Газпром / ...)
    fuel_type = db.Column(db.String(20))                    # тип топлива (АИ-92 / АИ-95 / ...)


    car = db.relationship('Car', backref='fillups')

    def __repr__(self):
        return f'<Fillup {self.date} {self.liters}L>'


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
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Добавить запись</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <a href="/services" class="back-link">← К списку</a>
            <h1>➕ Добавить запись об обслуживании</h1>

            <form method="POST">
                <p>
                    <label>Дата:
                        <input type="date" name="date" required>
                    </label>
                </p>
                <p>
                    <label>Пробег (км):
                        <input type="number" name="mileage" required>
                    </label>
                </p>
                <p>
                    <label>Тип работы:
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
                    <label>Описание (что делали):
                        <textarea name="description" rows="3"></textarea>
                    </label>
                </p>
                <p>
                    <label>Сервис:
                        <input type="text" name="workshop">
                    </label>
                </p>
                <p>
                    <label>Стоимость (₽):
                        <input type="number" name="cost">
                    </label>
                </p>
                <p>
                    <label>Следующее ТО (пробег, км):
                        <input type="number" name="next_service_mileage">
                    </label>
                </p>
                <p>
                    <button type="submit">Сохранить</button>
                </p>
            </form>
        </body>
        </html>
        '''


@app.route('/services/delete/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('services'))


@app.route('/fillups/new', methods=['GET', 'POST'])
def new_fillup():
    if request.method == 'POST':
        # Дата: если пустая — берём сегодня
        date_str = request.form.get('date', '').strip()
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.now().date()

        mileage = int(request.form['mileage'])
        liters = float(request.form['liters'])
        price_per_liter = float(request.form['price_per_liter'])

        # Сумма: если не указана — считаем сами
        total_cost_str = request.form.get('total_cost', '').strip()
        if total_cost_str:
            total_cost = int(total_cost_str)
        else:
            total_cost = int(liters * price_per_liter)

        gas_station = request.form.get('gas_station', '')
        fuel_type = request.form.get('fuel_type', 'АИ-95')

        car = Car.query.first()
        new_record = Fillup(
            car_id=car.id,
            date=date,
            mileage=mileage,
            liters=liters,
            price_per_liter=price_per_liter,
            total_cost=total_cost,
            gas_station=gas_station,
            fuel_type=fuel_type
        )

        db.session.add(new_record)
        db.session.commit()

        return redirect(url_for('fillups'))

    return '''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Добавить заправку</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <a href="/fillups" class="back-link">← К списку</a>
            <h1>➕ Добавить заправку</h1>

            <form method="POST">
                <p>
                    <label>Дата (необязательно, по умолчанию сегодня):
                        <input type="date" name="date">
                    </label>
                </p>
                <p>
                    <label>Пробег (км):
                        <input type="number" name="mileage" required>
                    </label>
                </p>
                <p>
                    <label>АЗС:
                        <select name="gas_station">
                            <option value="">— выбрать —</option>
                            <option value="Лукойл">Лукойл</option>
                            <option value="Газпром">Газпром</option>
                            <option value="Роснефть">Роснефть</option>
                        </select>
                    </label>
                </p>
                <p>
                    <label>Тип топлива:
                        <select name="fuel_type">
                            <option value="АИ-92">АИ-92</option>
                            <option value="АИ-95" selected>АИ-95</option>
                        </select>
                    </label>
                </p>
                <p>
                    <label>Литры:
                        <input type="number" name="liters" step="0.01" required>
                    </label>
                </p>
                <p>
                    <label>Цена за литр (₽):
                        <input type="number" name="price_per_liter" step="0.01" required>
                    </label>
                </p>
                <p>
                    <label>Общая стоимость (₽, необязательно — посчитается автоматически):
                        <input type="number" name="total_cost">
                    </label>
                </p>
                <p>
                    <button type="submit">Сохранить</button>
                </p>
            </form>
        </body>
        </html>
        '''


@app.route('/fillups/delete/<int:fillup_id>', methods=['POST'])
def delete_fillup(fillup_id):
    fillup = Fillup.query.get_or_404(fillup_id)
    db.session.delete(fillup)
    db.session.commit()
    return redirect(url_for('fillups'))



@app.route('/')
def home():
    car = Car.query.first()
    if car is None:
        return '<h1>Машина пока не добавлена</h1>'

    return f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Мой Селтос</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <h1>🚗 Мой автомобиль</h1>

        <div class="nav-menu">
            <a href="/services">📋 Обслуживание</a>
            <a href="/fillups">⛽️ Заправки</a>
        </div>
        <div class="car-card">
            <img src="/static/inside_car_sunset.jpg" alt="Моя ласточка">
            <div class="car-info">
                <p><b>Марка:</b> {car.brand}</p>
                <p><b>Модель:</b> {car.model}</p>
                <p><b>Год:</b> {car.year}</p>
                <p><b>Двигатель:</b> {car.engine}</p>
                <p><b>Коробка:</b> {car.transmission}</p>
                <p><b>Цвет:</b> {car.color}</p>
                <p><b>Текущий пробег:</b> {car.current_mileage} км</p>
            </div>
        </div>

        
    </body>
    </html>
    '''


@app.route('/services')
def services():
    all_services = Service.query.order_by(Service.date.desc()).all()

    if not all_services:
        return '''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Обслуживание</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <a href="/" class="back-link">← На главную</a>
            <h1>📋 Обслуживание</h1>
            <p>Записей пока нет</p>
            <div class="nav-menu">
                <a href="/services/new">➕ Добавить запись</a>
            </div>
        </body>
        </html>
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
            <td>
                <form method="POST" action="/services/delete/{s.id}" style="display: inline;" onsubmit="return confirm('Точно удалить?');">
                    <button type="submit" class="delete-btn">🗑️</button>
                </form>
            </td>
        </tr>
        '''

    return f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Обслуживание</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <a href="/" class="back-link">← На главную</a>
        <h1>📋 Обслуживание</h1>
        <div class="nav-menu">
            <a href="/services/new">➕ Добавить запись</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Дата</th>
                    <th>Пробег</th>
                    <th>Тип</th>
                    <th>Описание</th>
                    <th>Сервис</th>
                    <th>Стоимость</th>
                    <th>Действия</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    '''

@app.route('/fillups')
def fillups():
    all_fillups = Fillup.query.order_by(Fillup.date.desc()).all()

    if not all_fillups:
        return '''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Заправки</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <a href="/" class="back-link">← На главную</a>
            <h1>⛽️ Заправки</h1>
            <p>Записей пока нет</p>
            <div class="nav-menu">
                <a href="/fillups/new">➕ Добавить заправку</a>
            </div>
        </body>
        </html>
        '''

    rows = ''
    for f in all_fillups:
        rows += f'''
        <tr>
            <td>{f.date}</td>
            <td>{f.mileage} км</td>
            <td>{f.gas_station or '—'}</td>
            <td>{f.fuel_type or '—'}</td>
            <td>{f.liters} л</td>
            <td>{f.price_per_liter} ₽/л</td>
            <td>{f.total_cost} ₽</td>
            <td>
                <form method="POST" action="/fillups/delete/{f.id}" style="display: inline;" onsubmit="return confirm('Точно удалить?');">
                    <button type="submit" class="delete-btn">🗑️</button>
                </form>
            </td>
        </tr>
        '''

    return f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Заправки</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <a href="/" class="back-link">← На главную</a>
        <h1>⛽️ Заправки</h1>
        <div class="nav-menu">
            <a href="/fillups/new">➕ Добавить заправку</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Дата</th>
                    <th>Пробег</th>
                    <th>АЗС</th>
                    <th>Топливо</th>
                    <th>Литры</th>
                    <th>Цена/л</th>
                    <th>Сумма</th>
                    <th>Действия</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    '''



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

