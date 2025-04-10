from flask import Flask, render_template, redirect, url_for, session, request
import os
from sync_asinc_weather import get_weather
import requests
import json
import re

BASE_DIR = os.getcwd()

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

app = Flask(__name__, static_folder='static')

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
    return render_template('index.html', user_auth = 'user' not in session)


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
    city = response["name"]
    weather = response["weather"][0]["main"]
    degrees1 = f"{round((float(response["main"]["temp"]) - 273.15), 2)}°C"
    degrees2 = f"{round((float(response["main"]["feels_like"]) - 273.15), 2)}°C"
    user_text = f"Welcome back, {session['user']}!"
    return render_template("weather_minsk.html", city=city, weather=weather, degrees1=degrees1,
                               degrees2=degrees2, user_text = user_text)


@app.route('/weather/<city>/')
@login_required
def weather_city(city):
    try:
        response = get_weather(city)
        city = response["name"]
        weather = response["weather"][0]["main"]
        degrees1 = f"{round((float(response["main"]["temp"]) - 273.15), 2)}°C"
        degrees2 = f"{round((float(response["main"]["feels_like"]) - 273.15), 2)}°C"
        user_text = f"Welcome back, {session['user']}!"
        return render_template("weather_city.html", city=city, weather=weather, degrees1=degrees1,
                               degrees2=degrees2, user_text = user_text)
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
        user = {}
        user['login'] = request.form.get('login123')
        user['pas'] = request.form.get('password123')
        user['name'] = request.form.get('name123')
        user['email'] = request.form.get('email123')
        user['age'] = request.form.get('agel123')
        err = []
        with open('users.json', 'r', encoding='utf-8') as json_file:
            try:
                new_data = json.load(json_file)
                for us in new_data:
                    if user['login'] == us['login']:
                        err.append("User existed")
                        return render_template('registration.html', err=err)
            except json.JSONDecodeError:
                new_data = []
        session['user'] = user['login']
        session['pas'] = user['pas']
        session['name'] = user['name']
        session['email'] = user['email']
        session['age'] = user['age']
        if not re.match(r'^[a-zA-Z\d_]{6,20}$', user['login']):
            err.append("Incorrect login")
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[A-Z]).{8,15}$', user['pas']):
            err.append("Incorrect password")
        if not re.match(r'^[А-Яа-яЁё\s]+$', user['name']):
            err.append("Incorrect name and surname")
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', user['email']):
            err.append("Incorrect email")
        if not re.match(r'^\d+$', user['age']):
            err.append("Incorrect age")
        if err:
            return render_template('registration.html', err=err,
                                   age_field=session.get('age'),
                                   email_field=session.get('email'),
                                   name_field=session.get('name'),
                                   pas_field=session.get('pas'),
                                   user_field=session.get('user'))
        new_data.append(user)
        with open('users.json', 'w', encoding='utf-8') as json_file:
            json.dump(new_data, json_file)
        return redirect(url_for('index'))
    return render_template('registration.html')


@app.route("/logout/", methods=['GET', 'POST'])
def logout():
    session.pop('user', None)  # Удаляем 'user' из сессии
    return redirect(url_for('index'))


@app.route("/hw_4/")
@login_required
def hw_4():
    user_text = f"Welcome back, {session['user']}!"
    return render_template('hw_4.html', user_text = user_text)


@app.errorhandler(404)
def page_not_found():
    return '<h1 style="color:red">такой страницы не существует</h1>'


app.run(debug=True)