import requests
import time

URL = "https://твой-сервис.onrender.com"  # URL из Render

while True:
    try:
        requests.get(URL)
        print("Пинг отправлен")
    except:
        pass
    time.sleep(600)  # 10 мин
