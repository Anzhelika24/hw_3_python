from bs4 import BeautifulSoup
with open ("example.html", "r", encoding="utf_8") as file:
    text = file.read()

soup = BeautifulSoup(text, 'html.parser')

titles = soup.find('title')
print(titles.text)