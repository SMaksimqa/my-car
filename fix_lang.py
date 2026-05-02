from app import app, db, Car

with app.app_context():
    car = Car.query.first()
    car.engine = "1.6 бензин"
    car.transmission = "МКПП"
    db.session.commit()
    print(f"Updated: {car.engine}, {car.transmission}")
