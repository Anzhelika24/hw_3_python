from bs4 import BeautifulSoup
with open ("wiki.html", "r", encoding="utf_8") as file:
    text = file.read()

soup = BeautifulSoup(text, 'html.parser')

links = soup.find_all('a', attrs={'href': True})

result = []
for link in links:
    result.append(f"{link.text}: {link.attrs['href']}")

text_new = '\n'.join(result)

with open("links.txt", "w", encoding='utf_8') as f:
    f.write(text_new)
# print(result, '\n')
# print(text_new)
