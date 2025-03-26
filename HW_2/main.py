from flask import Flask, render_template
import os
from sync_asinc_weather import get_weather
import requests

BASE_DIR = os.getcwd()

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))


def get_method(base_url):
    response = requests.request('GET', base_url)
    return response

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/duck/")
def duck():
    response = get_method("https://random-d.uk/api/random")
    response = response.json()
    return render_template("duck.html", h = response["url"])


@app.route("/fox/<int:num>/")
def fox(num):
    if 1<=num<=10:
        images = []
        for x in range(num):
            response = get_method("https://randomfox.ca/floof/")
            response = response.json()
            images.append(response["image"])
        return render_template("fox.html", images = images)
    else:
        return render_template("fox.html", text = "true")


@app.route("/weather-minsk/")
def weather_minsk():
    response = get_weather('Minsk')
    return render_template("weather_minsk.html", response = response)


@app.route('/weather/<city>/')
def weather_city(city):
    response = get_weather(city)
    return render_template("weather_city.html", response = response)


@app.errorhandler(404)
def page_not_found(error):
    return '<h1 style="color:red">такой страницы не существует</h1>'


app.run(debug=True)