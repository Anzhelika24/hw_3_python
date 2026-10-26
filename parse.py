from bs4 import BeautifulSoup
with open ("wiki.html", "r", encoding="utf_8") as file:
    text = file.read()

soup = BeautifulSoup(text, 'html.parser')

titles = soup.find_all('title')
# print(titles)
result = []
for title in titles:
    result.append(title.text)
text_new = '/n'.join(result)
print(result)
print(text_new)
