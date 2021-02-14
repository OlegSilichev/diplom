from app import app, db
from app.models import User, Car, Rental_log
from flask import render_template, request, url_for, redirect, flash, session, abort, make_response
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime
import os
import sys



# Отображение информации на странице в зависимоти от авторизованного пользователя
def user_info(id):
    user = User.query.get(id)
    context = {'id': id,
        'name': f'{user.name} {user.last_name}',             
    }
    return context

# Список всех автомобилей сервиса
def car_list_all():
    car_all = Car.query.all()
    car_dict = {'car_list': car_all}
    return car_dict

# Проверка url адреса на правильный id авторизованного пользователя
def id_check_url(id):
    if int(current_user.get_id()) != id:
        return abort(404)

# Проверка загружаемых изображений автомобилей в базу данных
def chesk_img(img):
    img.flush()
    if os.fstat(img.fileno()).st_size < 1048577:
        if bool(img) and img.content_type == "image/jpeg" :
            sys.stdout.flush()
            return img.read()
    else:
        sys.stdout.flush()  
        return None

# Проверка что пользователь вошел под учетной записью администратора
def admin_check():
    if current_user.is_active and current_user.get_id() == "3" and current_user.password == 'pbkdf2:sha256:150000$mrwUbNCS$43eb7e0d9c6ff0056b93a491f0dec08455d902ed6c0809cdb7b0574aa278d084':
        return True
    else:
        return False

# Начальная страница без авторизации
@app.route('/index')
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(f'/user_index/{current_user.get_id()}')
    return render_template('index.html', **car_list_all())

# Начальная страница пользователя, который авторизовался
@app.route('/user_index/<int:id>')
@login_required
def user_index(id):
    id_check_url(id)
    u_info = {}
    u_info = user_info(id)
    if admin_check():
        u_info['panel'] = 'Управление'
        u_info['link'] = f'/admin_panel/{ id }'
    else:
        u_info['panel'] = 'Главная'
        u_info['link'] = '/'
    u_info.update(car_list_all())
    return render_template('/user_index.html', **u_info)
    
# Детальная страница автомобиля
@app.route('/auto_detail/<int:id>')
def auto_detail(id):
    context = {'car_info': Car.query.get(id)}
    return render_template('auto_detail.html', **context)

# Детальная страница автомобиля для авторизованного пользователя
@app.route('/user_auto_detail/<int:id>/<int:carid>', methods=['POST','GET'])
@login_required
def user_auto_detail(id, carid):
    user_log = (User.query.get(id)).rental_log.order_by(Rental_log.start_rental_time.desc()).filter_by(car_id=carid).all()
    context = {'car_info': Car.query.get(carid),
               'user_info': user_info(id),
               'user_log': user_log
    }
    if request.method == 'POST':
        return redirect(f'/change_auto/{id}/{carid}')
    else:
        return render_template('user_auto_detail.html', **context)

# Страница добавление автомобиля
@app.route('/create_auto/<int:id>', methods=['POST', 'GET'])
@login_required
def create_auto(id):
    id_check_url(id)
    if admin_check():                
        if request.method == "POST":
            name_car = request.form['name_car']
            description = request.form['description']
            rental_price = request.form['rental_price']
            transmission = bool(request.form['transmission'])
            picture1 = chesk_img(request.files['file1'])
            picture2 = chesk_img(request.files['file2'])
            picture3 = chesk_img(request.files['file3'])
            picture4 = chesk_img(request.files['file4'])
            if picture1 is not None and picture2 is not None and picture3 is not None and picture4 is not None:                    
                car = Car(name_car, description, rental_price, transmission, picture1, picture2, picture3, picture4)
                db.session.add(car)
                db.session.commit()            
                flash(f"Автомобиль в базу добавлен")
                return render_template('create_auto.html',**user_info(id))
            else:
                flash(f"При загрузке фотографий не соблюдены параметры!!!")
                return render_template('create_auto.html',**user_info(id))            
        elif request.method == "GET":
            return render_template('create_auto.html',**user_info(id))      
    else:
        return abort(404)

# Удаление автомобиля со всеми журналами
@app.route('/delete_auto/<int:id>', methods=['POST'])
@login_required
def delete_auto(id):
    if request.method == 'POST':
        auto = Car.query.get(id)
        db.session.delete(auto)
        db.session.commit()
        return redirect(f'/car_list/{current_user.get_id()}')

# Страница изменения информации об автомобиле
@app.route('/change_auto/<int:id>/<int:car_id>', methods=['POST','GET'])
@login_required
def change_auto(id,car_id):
    id_check_url(id)
    if admin_check():
        auto = Car.query.get(car_id)
        context = {'user_info': user_info(id),
                   'auto': auto
        }
        if request.method == 'POST':
            auto.name_car = request.form['name_car']            
            auto.description = request.form['description']            
            auto.rental_price = request.form['rental_price']
            auto.transmission = bool(request.form['transmission'])
            picture1 = chesk_img(request.files['file1'])
            if picture1 is not None:
                auto.picture1 = picture1
            picture2 = chesk_img(request.files['file2'])
            if picture2 is not None:
                auto.picture2 = picture2
            picture3 = chesk_img(request.files['file3'])
            if picture3 is not None:
                auto.picture3 = picture3
            picture4 = chesk_img(request.files['file4'])
            if picture4 is not None:
                auto.picture4 = picture4
            db.session.commit()
            return redirect(f'/user_auto_detail/{id}/{car_id}')
        elif request.method == 'GET':
            return render_template('change_auto.html', **context)
    else:
        return abort(404)

# Страница журнала аренды всех автомобилей для авторизованного пользователя
@app.route('/user_rental_log/<int:id>')
@login_required
def user_rental_log(id):
    id_check_url(id)
    log = (User.query.get(id)).rental_log.all()
    context = {'user_info': user_info(id),
               'car_all': Car.query.all(),
               'log_all': log
    }
    return render_template('user_rental_log.html', **context)

# Страница журнала аренды всех автомобилей доступная из панели администратора
@app.route('/admin_rental_log/<int:id>')
@login_required
def admin_rental_log(id):
    id_check_url(id)
    if admin_check():
        context = {'id': current_user.get_id(),
                   'car_all': Car.query.all(),
                   'log_all': Rental_log.query.all()
        }
        return render_template('admin_rental_log.html', **context)
    else:
        return abort(404)

# Страница упраления, доступная только учетной записи администратора
@app.route('/admin_panel/<int:id>')
def admin_panel(id):
    id_check_url(id)
    if admin_check():
        user_list = User.query.all()
        context = {"id": current_user.get_id(), "user_list": user_list}
        return render_template('admin_panel.html', **context)
    else:
        return abort(404)

# Страница просмотра всех автомобилей
@app.route('/car_list/<int:id>')
def car_list(id):
    id_check_url(id)
    if admin_check():
        return render_template('car_list.html', id=current_user.get_id(), **car_list_all())
    else:
        return abort(404)
 
# Страница регистрации
@app.route('/reg_form', methods=['POST', 'GET'])
def reg_form():
    if request.method == "POST":
        if len(request.form['password']) >= 8:
            if request.form['password'] == request.form['chesk_password']:
                name = request.form['name']
                last_name = request.form['last_name']
                age = request.form['age']
                email = (request.form['email']).lower()
                phone_number = request.form['phone_number']
                password = request.form['password']
                try:
                    user = User.query.filter_by(email=email).first()
                    if user is None:
                        user = User(name, last_name, age, email, phone_number, password)
                        db.session.add(user)
                        db.session.commit()
                        login_user(user)
                        return redirect(f"/user_index/{user.id}")
                    else:
                        flash('Данный пользователь уже существует. Укажите другой email.')
                        return redirect('/reg_form')
                except:
                    flash('Произошла какая то неизвестная ошибка')
                    return render_template('reg_form.html')
            else:
                flash("Пароли не совпадают")
                return render_template('reg_form.html')
        else:
            flash("Пароль слишком короткий. Длина пароля менее 8 символов!")
            return render_template('reg_form.html')
    elif request.method == "GET":
        return render_template('reg_form.html')

# Страница авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()
        password = request.form['password']
        remember = True if request.form.get('remember') else False
        if (user is not None) and (User.check_password(user.password, password)):
            login_user(user, remember=remember)
            try:
                next = request.args.get("next")
                next = next.replace('rental/x', f'user_auto_detail/{user.id}')
                return redirect(next)
            except AttributeError:
                return redirect(f"/user_index/{user.id}")
        else:
            flash(f"Данный пользователь не найден.")
            return redirect(url_for('login', next=request.args.get("next")))
    elif request.method == "GET":
        return render_template('login.html')

# Выход из сессии
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Преобразование изображения автомобиля из базы данных в читаемый формат
@app.route('/get_img/<int:id>/<int:num>')
def get_img(id,num):
    img = (Car.query.filter_by(id=id).first()).get_image[num]
    picture = make_response(img)
    picture.headers['Content-Type'] = "image/jpeg"
    return picture

# Пользователь нажал кнопку арендовать
@app.route('/rental/<path:id>/<int:car_id>', methods=['POST'])
@login_required
def rental(id, car_id):
    car = Car.query.filter_by(user=int(id)).first()
    if car is None: # Нажали Арендовать
        car = Car.query.get(car_id)
        car.rental_status = True
        car.user = int(id)
        car.start_rental_time = datetime.now()
        db.session.commit()
        return redirect(url_for('user_auto_detail', id=int(id), carid=car_id))
    elif car.id == car_id and car.rental_status == True: # Нажали завершить аренду
        car = Car.query.get(car_id)
        rental_cost = ((datetime.now() - car.start_rental_time).seconds // 60) * car.rental_price
        log = Rental_log(id, car_id, car.start_rental_time, datetime.now(), rental_cost)
        db.session.add(log)
        car.rental_status = False
        car.user = 0
        car.start_rental_time = None
        db.session.commit()
        return redirect(url_for('user_auto_detail', id=int(id), carid=car_id))
    else: 
        flash('Вы не можете арендовать больше одной машины. Завершите аренду текущей!')
        return redirect(url_for('user_auto_detail', id=int(id), carid=car.id))

# Страница о сайте
@app.route('/about')
def about():
    return render_template('about.html')

# Вывод страницы при запросе не существующей
@app.errorhandler(404)
def error404(error):
    return render_template('error404.html'), 404
    