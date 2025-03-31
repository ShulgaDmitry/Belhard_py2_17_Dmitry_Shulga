from flask import Flask, render_template, redirect, url_for, session, request
import os
from sync_asinc_weather import get_weather
import requests
import json

BASE_DIR = os.getcwd()

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))


app.secret_key = os.urandom(24)


def get_method(base_url):
    response = requests.request('GET', base_url)
    return response


def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Сохранение имени оригинальной функции
    return wrapper


@app.route("/")
def index():
    if 'user' not in session:
        return render_template('index.html', user_auth = "true")
    else:
        return render_template('index.html', user_auth = "false")


@app.route("/duck/")
@login_required
def duck():
    response = get_method("https://random-d.uk/api/random")
    response = response.json()
    user_text = f"Welcome back, {session['user']}!"
    return render_template("duck.html", h = response["url"], user_text = user_text)


@app.route("/fox/<int:num>/")
@login_required
def fox(num):
    if 1<=num<=10:
        images = []
        for x in range(num):
            response = get_method("https://randomfox.ca/floof/")
            response = response.json()
            images.append(response["image"])
        user_text = f"Welcome back, {session['user']}!"
        return render_template("fox.html", images = images, user_text = user_text)
    else:
        return render_template("fox.html", text = "true")


@app.route("/weather-minsk/")
@login_required
def weather_minsk():
    response = get_weather('Minsk')
    user_text = f"Welcome back, {session['user']}!"
    return render_template("weather_minsk.html", response = response, user_text = user_text)


@app.route('/weather/<city>/')
@login_required
def weather_city(city):
    try:
        response = get_weather(city)
        user_text = f"Welcome back, {session['user']}!"
        return render_template("weather_city.html", response=response, user_text = user_text)
    except Exception as e:
        return render_template("weather_city.html", text = "true")


@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = {}
        user['login'] = request.form.get('login123')
        user['pas'] = request.form.get('password123')
        with open('users.json', 'r', encoding='utf-8') as json_file:
            try:
                new_data = json.load(json_file)
                for us in new_data:
                    if user['login'] == us['login'] and user['pas'] == us['pas']:
                        session['user'] = user['login']
                        return redirect(url_for('index'))
                    else:
                        err = []
                        err.append("User does not exist")
                        return render_template('registration.html', err=err)
            except json.JSONDecodeError:
                err = []
                err.append("User does not exist")
                return render_template('registration.html', err=err)
    else:
        return render_template('login.html')


@app.route("/registration/", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        user={}
        user['login'] = request.form.get('login123')
        user['pas'] = request.form.get('password123')
        user['name'] = request.form.get('name123')
        user['email'] = request.form.get('email123')
        user['age'] = request.form.get('agel123')
        with open('users.json', 'r', encoding='utf-8') as json_file:
            try:
                new_data = json.load(json_file)
                for us in new_data:
                    if user['login'] == us['login']:
                        err = []
                        err.append("User existed")
                        return render_template('registration.html', err=err)
            except json.JSONDecodeError:
                new_data = []
        err = []
        session['user'] = user['login']
        session['pas'] = user['pas']
        session['name'] = user['name']
        session['email'] = user['email']
        session['age'] = user['age']
        if (6 <= len(user['login']) <= 20 and any(char.isdigit() for char in user['login']) and
                any(char.isalpha() for char in user['login']) and '_' in user['login']):
            if (8<=len(user['pas'])<= 15 and any(char.isdigit() for char in user['pas']) and
                any(char.isalpha() for char in user['pas']) and any(char.isupper() for char in user['pas'])):
                if all('А' <= char <= 'я' or char in 'Ёё ' for char in user['name']):
                    if '@' in user['email'] and '.' in user['email']:
                        if all(char.isdigit() for char in user['age']):
                            new_data.append(user)
                            with open('users.json', 'w', encoding='utf-8') as json_file:
                                json.dump(new_data, json_file)
                            return redirect(url_for('index'))
                        else:
                            err.append("Incorrect age")
                            age_field = session['age']
                            email_field = session['email']
                            name_field = session['name']
                            user_field = session['user']
                            pas_field = session['pas']
                            return render_template('registration.html', err=err, age_field=age_field,
                                                   email_field=email_field, name_field = name_field,
                                                   pas_field = pas_field, user_field = user_field)
                    else:
                        err.append("Incorrect email")
                        email_field = session['email']
                        name_field = session['name']
                        user_field = session['user']
                        pas_field = session['pas']
                        return render_template('registration.html', err=err,email_field=email_field,
                                               name_field=name_field, pas_field=pas_field, user_field=user_field)
                else:
                    err.append("Incorrect name and surname")
                    name_field = session['name']
                    user_field = session['user']
                    pas_field = session['pas']
                    return render_template('registration.html', err=err,name_field=name_field,
                                           pas_field=pas_field, user_field=user_field)
            else:
                err.append("Incorrect password")
                user_field = session['user']
                pas_field = session['pas']
                return render_template('registration.html', err=err, pas_field=pas_field,
                                       user_field=user_field)
        else:
            err.append("Incorrect login")
            user_field = session['user']
            return render_template('registration.html', err=err,user_field=user_field)
    else:
        return render_template('registration.html')


@app.route("/logout/", methods=['GET', 'POST'])
def logout():
    session.pop('user', None)  # Удаляем 'user' из сессии
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return '<h1 style="color:red">такой страницы не существует</h1>'


app.run(debug=True)