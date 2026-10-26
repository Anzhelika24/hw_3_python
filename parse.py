from bs4 import BeautifulSoup
with open ("wiki.html", "r", encoding="utf_8") as file:
    text = file.read()

soup = BeautifulSoup(text, 'html.parser')

links = soup.find_all('a', attrs={'href': True})

result = []
for link in links:
    result.append(link.attrs['href'])
text_new = '\n'.join(result)
print(result)
print(text_new)
