from bs4 import BeautifulSoup
with open ("wiki.html", "r", encoding="utf_8") as file:
    text = file.read()

soup = BeautifulSoup(text, 'html.parser')

links = soup.find_all('a', attrs={'href': True})

result = []
for link in links[:10]:
    result.append(f"{link.text}: {link.attrs['href']}")

text_new = '\n'.join(result)
# print(result, '\n')
print(text_new)
