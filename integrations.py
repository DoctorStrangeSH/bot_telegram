# integrations.py
import aiohttp
from datetime import datetime, timezone, timedelta

MOSCOW_TZ = timezone(timedelta(hours=3))

class WeatherAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    async def get_weather(self, city="Moscow"):
        """Получение погоды"""
        if not self.api_key:
            return "API ключ не настроен"
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "ru"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        temp = data['main']['temp']
                        description = data['weather'][0]['description']
                        return f"🌤 Погода в {city}:\nТемпература: {temp}°C\n{description.capitalize()}"
                    else:
                        return "Не удалось получить погоду"
        except Exception as e:
            return f"Ошибка: {e}"

class CurrencyAPI:
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    async def get_rates(self):
        """Получение курсов валют"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rates = data['rates']
                        return {
                            "USD": rates.get('RUB', 'N/A'),
                            "EUR": rates.get('RUB', 0) / rates.get('EUR', 1),
                        }
        except Exception as e:
            return None
    
    async def get_currency_message(self):
        """Форматированное сообщение о курсах"""
        rates = await self.get_rates()
        if rates:
            return f"💱 Курсы валют:\nUSD: {rates['USD']:.2f} RUB\nEUR: {rates['EUR']:.2f} RUB"
        return "Не удалось получить курсы"

weather_api = WeatherAPI()
currency_api = CurrencyAPI()