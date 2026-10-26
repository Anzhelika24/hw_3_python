import requests

response = requests.get("https://example.com", timeout=10)
response.raise_for_status()

with open("example.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("Страница сохранена")

