import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

def create_main_html(domain):
    response = requests.get(domain, timeout=10)
    response.raise_for_status()

    with open(f"wiki.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    print("Страница сохранена")

def complete_url(relative_url, domain):
    full_url = urljoin(domain, relative_url)
    return full_url

def the_course_is_empty(link):
    if 'class' in link.attrs and 'new' in link.attrs['class']:
        return True 

domain = "https://wiki.atp-fivt.org/"

if not Path('wiki.html').is_file():
    create_main_html(domain)

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

unique_adresses = set()

courses = {
    "Весенний семестр 2025 года": {},
    "Осенний семестр 2025 года": {},
    "Весенний семестр 2026 года": {},
    "Осенний семестр 2026 года": {},
}

headlines = soup.find_all('span', attrs={'class': 'mw-headline'})
#236
for headline in headlines:
    head_text = headline.text
    if ('2025' in head_text or '2026' in head_text):
        heading = headline.parent
        for neighbour in heading.find_next_siblings():
            if neighbour.name == 'h3':
                break
            if neighbour.name == 'table':
                links = neighbour.find_all('a', href=lambda href: href and not href.startswith('#'))
                for link in links:
                    if not the_course_is_empty(link):
                        relative_url = link.attrs['href']
                        full_url = complete_url(relative_url, domain)
                        courses[head_text][full_url] = link.text

count = 0
for _, semester_courses in courses.items():
    for course_url, _ in semester_courses.items():
        count += 1
        unique_adresses.add(course_url)

print(f'было: {count}, стало: {len(unique_adresses)}')
        

with open('headlines.txt', 'w', encoding='utf_8') as file:
    for semester_name, semester_courses in courses.items():
        file.write(semester_name + '\n\n')
        for course_url, name_course in semester_courses.items():
            file.write(f'{name_course}: {course_url}' + '\n')
# print(result, '\n')
# print(text_new)
