from FlightRadarAPI import FlightRadar24
import math
import time
import requests
import winsound

# Функция автоматического определения координат по IP
def get_my_location():
    try:
        # Бесплатный публичный API для определения геолокации по IP
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        if data["status"] == "success":
            lat = data["lat"]
            lon = data["lon"]
            city = data["city"]
            country = data["country"]
            print(f"Твоя локация успешно определена, сука: {country}, {city} (Широта: {lat}, Долгота: {lon})")
            return lat, lon
        else:
            print("Не удалось определить координаты по IP, использую дефолтные.")
            return 55.7558, 37.6173  # Москва по умолчанию, если что
    except Exception as e:
        print(f"Ошибка геолокации: {e}, использую дефолтные координаты.")
        return 55.7558, 37.6173

# Получаем координаты при старте программы
MY_LAT, MY_LON = get_my_location()
ALERT_RADIUS_KM = 30  # Радиус тревоги в километрах

fr_api = FlightRadar24()

def calculate_distance(lat1, lon1, lat2, lon2):
    """Считает расстояние между двумя точками в километрах"""
    R = 6371  # Радиус Земли в км
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

print("\nСистема авто-ПВО запущена, сука! Сканируем небо вокруг тебя...")

while True:
    try:
        flights = fr_api.get_flights()
        target_found = False

        for flight in flights:
            if flight.latitude and flight.longitude:
                # Считаем расстояние от текущих координат до самолета
                dist = calculate_distance(MY_LAT, MY_LON, flight.latitude, flight.longitude)
                
                if dist <= ALERT_RADIUS_KM:
                    target_found = True
                    print(f"⚡ ВНИМАНИЕ! Близкая цель! Рейс: {flight.number} | Позывной: {flight.callsign} | Расстояние: {dist:.1f} км | Высота: {flight.altitude} футов")
                    
                    # Пищим системным динамиком
                    winsound.Beep(2500, 400)

        if not target_found:
            print("Небо над тобой чистое, целей в радиусе нет...")

        print("-" * 40)
        time.sleep(15) # Пауза перед следующим сканированием
        
    except Exception as e:
        print(f"Пиздец, ошибка при сканировании: {e}")
        time.sleep(10)
