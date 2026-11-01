from bs4 import BeautifulSoup
import json

def parse_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

filename = (
    "courses_2025_2026/"
    "Применение Python в статистическом анализе данных_Осень_2026.html"
)

soup = parse_html_file(filename)
content = soup.find(attrs={"class": "mw-parser-output"})
with open('python_course.txt', 'w', encoding='utf-8') as f:
    f.write(soup.find('h1').text + '\n')
    f.write(content.text)


def extract_sections(content):
    sections = {}
    heading_tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
    for label in content.find_all('span', attrs={'class': 'mw-headline'}):
        heading = label.parent
        section_name = label.text.strip()
        parts = []
        for neighbour in heading.find_next_siblings():
            if neighbour.name in heading_tags:
                if neighbour.name[1] <= heading.name[1]:
                    break
            parts.append(neighbour.text)
        sections[section_name] = '\n'.join(parts).strip()
    return sections

json_sections = extract_sections(content)

with open('python_course_sections.json', 'w', encoding='utf-8') as f:
    json.dump(json_sections, f, ensure_ascii=False, indent=4)




