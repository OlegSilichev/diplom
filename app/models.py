from app import db
from flask_login import UserMixin
from datetime import datetime



# Пакет для хэширования паролей
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """Таблица User. Содержит данные о пользователях сервиса твой каршеринг """
    
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    password = db.Column(db.String(100))
    date_time = db.Column(db.DateTime, default=datetime.now)
    rental_log = db.relationship('Rental_log', backref='user', lazy='dynamic')

    def __init__(self, name, last_name, age, email, phone_number, password):
            self.name = name
            self.last_name = last_name
            self.age = age
            self.email = email
            self.phone_number = phone_number
            self.password = User.set_password(self, password)
                  
    # Получаем хэш из пароля
    def set_password(self, password):
        password_hash = generate_password_hash(password)
        return password_hash
    
    # Проверка на правильность ввода пароля
    def check_password(self, password):
        return check_password_hash(self, password)

class Car(db.Model):
    """Таблица Car. Содержит данные об автомобилях """
    
    __tablename__ = 'car'

    id = db.Column(db.Integer, primary_key=True)
    name_car = db.Column(db.String(100))
    description = db.Column(db.String(100))
    rental_price = db.Column(db.Float)
    transmission = db.Column(db.Boolean)
    rental_status = db.Column(db.Boolean, default=False)
    picture1 = db.Column(db.LargeBinary)
    picture2 = db.Column(db.LargeBinary)
    picture3 = db.Column(db.LargeBinary)
    picture4 = db.Column(db.LargeBinary)
    user = db.Column(db.Integer, default=0)
    rental_log = db.relationship('Rental_log', backref='car', cascade='all,delete', lazy='dynamic')
    start_rental_time = db.Column(db.DateTime, default=None)
    end_rental_time = db.Column(db.DateTime, default=None)
                  
    def __init__(self, name_car, description, rental_price, transmission, picture1, picture2, picture3, picture4):
            self.name_car = name_car
            self.description = description
            self.rental_price = rental_price
            self.transmission = transmission
            self.picture1 = picture1
            self.picture2 = picture2
            self.picture3 = picture3
            self.picture4 = picture4
    
    # Получаем кортедж изображений
    @property
    def get_image(self):
        return self.picture1, self.picture2, self.picture3, self.picture4

class Rental_log(db.Model):
    """Таблица Rental_log. Содержит данные об аренде конкретного автомобиля, конкретным пользователем. """

    __tablename__ = 'rental_log'
        
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer(), db.ForeignKey('car.id'), nullable=False)
    start_rental_time = db.Column(db.DateTime)
    end_rental_time = db.Column(db.DateTime)
    cost_rental = db.Column(db.Float)
    def __init__(self, user_id, car_id, start_rental_time, end_rental_time, cost_rental):
        self.user_id = user_id
        self.car_id = car_id
        self.start_rental_time = start_rental_time
        self.end_rental_time = end_rental_time
        self.cost_rental = cost_rental
          