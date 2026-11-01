from bs4 import BeautifulSoup
import json
import re
from pathlib import Path 
from download import collect_courses, take_unique_adresses

def parse_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

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


def find_contacts(content):
    pattern_mail = r'[\w\.-]+@[\w\.-]+'
    emails = re.findall(pattern_mail, content.text)
    cleaned_emails = list(set(email.strip('.,') for email in emails))

    telegram_links = []
    for link in content.find_all('a', attrs={'href': True}):
        if 't.me/' in link['href']:
            telegram_links.append(link['href'])
    telegram_links = list(set(telegram_links))

    return cleaned_emails + telegram_links

def counting_homeworks(content):
    patterns = [
    r'(?:запланировано|всего)\s+(\d+)\s+домашних\s+заданий',
    r'(?:запланировано|всего)\s+домашних\s+заданий\s*[:—–-]?\s*(\d+)',
]
    for pattern in patterns:
        match = re.search(pattern, content.text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

def create_dict_for_course_info(soup):
    content = soup.find(attrs={"class": "mw-parser-output"})
    course_info = {}
    if content is None:
        course_info['sections'] = {}
        course_info['full_text'] = soup.text.strip()
        course_info['title'] = soup.find(attrs={"class": "mw-page-title-main"})
        course_info['parse_status'] = 'unsupported format'
        return course_info
    course_info = {'title': None, 'assessment': None, 'has_course_plan': None, 'course_leader': None, 'has_contacts': None, 'contacts': None, 
                   'homework_count': None}
    course_info['title'] = soup.find(attrs={"class": "mw-page-title-main"}).text.strip()
    sections = extract_sections(content)
    course_info['sections'] = sections
    course_info['full_text'] = content.text.strip()
    course_info['parse_status'] = 'ok'
    # pattern_assessment = r'оцен'
    # course_info['assessment'] = sections.get(pattern_assessment, None)
    course_info['assessment'] = sections.get('Форма контроля', None)
    course_info['has_course_plan'] = sections.get('План курса', None) is not None or sections.get('Программа курса', None) is not None
    course_info['course_leader'] = sections.get('Руководитель курса', None)
    course_info['contacts'] = find_contacts(content)
    course_info['has_contacts'] = bool(course_info['contacts'])
    course_info['homework_count'] = counting_homeworks(content)
    return course_info

def create_course_info_json():
    courses_info = {}
    main_soup = parse_html_file("wiki.html")
    courses = collect_courses(main_soup, "https://wiki.atp-fivt.org/")
    unique_adresses = take_unique_adresses(courses)
    for url, name in unique_adresses.items():
        safe_name = name.replace("/", "_")
        file_path = f'courses_2025_2026/{safe_name}.html'

        soup = parse_html_file(file_path)
        course_info = create_dict_for_course_info(soup)
        course_info['url'] = url
        courses_info[file_path] = course_info

    with open('courses_info.json', 'w', encoding='utf-8') as f:
        json.dump(courses_info, f, ensure_ascii=False, indent=4)

create_course_info_json()
