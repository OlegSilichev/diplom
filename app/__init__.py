from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager



# Создаем экземпляр класса flask 
app = Flask(__name__, static_url_path='', static_folder='static')

#Секретный ключ для работы с сессиями
app.config["SECRET_KEY"] = "3aff531836ab343dab366ed665e19c27beed5e31"

# Подключаем базу данных к приложению
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../diplom.sqlite"

# Отключаем вывод технических сообщений
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Создаем саму базу данных - объект db
db = SQLAlchemy(app)

# Создаем объект для работы с миграциями
migrate = Migrate(app, db)

# Создаем обьект для управления сессиями
login_manager = LoginManager(app)

# Перенаправляем на страницу login.html если неаторизованный пользователь обращается к защищенной странице
login_manager.login_view = "login"
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам либо зарегестрируйтесь"
login_manager.login_message_category = "success"

from app import views
from app import models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))
