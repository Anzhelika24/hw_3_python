import requests

response = requests.get("https://wiki.atp-fivt.org/", timeout=10)
response.raise_for_status()

with open("wiki.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("Страница сохранена")

