from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests

# Criando o Blueprint para o clima
weather_bp = Blueprint('weather', __name__, template_folder='templates/weather')

@weather_bp.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        city = request.form.get("city")
        api_key = "d77c765fe183231b80c00659032e10cf"
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        complete_url = f"{base_url}?q={city}&appid={api_key}&units=metric"
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != "404" and "name" in data:
            weather_data = {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
            }
            return render_template("weather/weather.html", weather_data=weather_data)
        else:
            flash("Cidade não encontrada. Tente novamente.")
            return redirect(url_for("weather.weather"))
    return render_template("weather/weather.html")