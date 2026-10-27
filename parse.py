from bs4 import BeautifulSoup
from urllib.parse import urljoin
with open ("wiki.html", "r", encoding="utf_8") as file:
    text = file.read()

def complete_url(relative_url):
    base_url = "https://wiki.atp-fivt.org" 
    full_url = urljoin(base_url, relative_url)
    return full_url

def the_course_is_empty(link):
    if 'class' in link.attrs and 'new' in link.attrs['class']:
        return True 

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


semesters = dict()
semesters['k'] = {'a'}
semesters['k'].add('b')
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
                        full_url = complete_url(relative_url)
                        courses[head_text][full_url] = link.text

with open('headlines.txt', 'w', encoding='utf_8') as file:
    for semester_name, semester_courses in courses.items():
        file.write(semester_name + '\n\n')
        for course_url, name_course in semester_courses.items():
            file.write(f'{name_course}: {course_url}' + '\n')
# print(result, '\n')
# print(text_new)
