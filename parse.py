from bs4 import BeautifulSoup
with open ("wiki.html", "r", encoding="utf_8") as file:
    text = file.read()

soup = BeautifulSoup(text, 'html.parser')

with open("pretty_wiki_html.html", "w", encoding='utf_8') as f:
    f.write(soup.prettify())

links = soup.find_all('a', href=lambda href: href and not href.startswith('#'))

result = []
for link in links:
    result.append(f"{link.text}: {link.attrs['href']}")

text_new = '\n'.join(result)

with open("links.txt", "w", encoding='utf_8') as f:
    f.write(text_new)

headlines = soup.find_all('span', attrs={'class': 'mw-headline'})
with open('headlines.txt', 'w', encoding='utf_8') as file:
    for headline in headlines:
        head_text = headline.text
        if ('2025' in head_text or '2026' in head_text):
            file.write(head_text + '\n\n')
            heading = headline.parent
            for neighbour in heading.find_next_siblings():
                if neighbour.name == 'h3':
                    break
                if neighbour.name == 'table':
                    links = neighbour.find_all('a', href=lambda href: href and not href.startswith('#'))
                    for link in links:
                        file.write(link.text + '\n')


# print(result, '\n')
# print(text_new)
