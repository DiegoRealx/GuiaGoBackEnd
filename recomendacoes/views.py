from django.shortcuts import render
import requests
from django.conf import settings

def weather_view(request):
    city = "Salvador"  
    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        temperature = data['main']['temp']  
        condition = data['weather'][0]['description']  
        humidity = data['main']['humidity'] 
        wind_speed = data['wind']['speed'] 
        
        translations = {
            "clear sky": "céu limpo",
            "few clouds": "poucas nuvens",
            "scattered clouds": "levemente nublado",
            "broken clouds": "parcialmente nublado",
            "overcast clouds": "nublado",
            "light rain": "chuva fraca",
            "moderate rain": "chuva moderada",
            "heavy intensity rain": "chuva forte",
            "light snow": "neve leve",
            "moderate snow": "neve moderada",
            "heavy snow": "neve pesada",
            "fog": "neblina",
            "mist": "névoa",
            "haze": "nevoeiro",
            "dust": "poeira",
            "sand": "areia",
            "ash": "cinzas",
            "squall": "rajada de vento",
            "tornado": "tornado",
        }
        
        translated_condition = translations.get(condition, condition) 

        return render(request, 'weather.html', {
            'temperature': temperature,
            'condition': translated_condition,
            'humidity': humidity,
            'wind_speed': wind_speed,
        })
    else:
        return render(request, 'error.html', {'message': 'Não foi possível obter dados do tempo.'})
