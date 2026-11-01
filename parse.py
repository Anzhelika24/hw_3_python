from bs4 import BeautifulSoup
import json
import re
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


def get_number_homeworks_by_counting_matches(content):
    text = content.text

    pattern = (
        r'\b(?:мини-)?дз[ \t]*[№#]?[ \t]*\d+\b|мини-дз[ \t]+[^\n]+'
    )

    names = re.findall(pattern, text, flags=re.IGNORECASE)
    homeworks = set()
    for name in names:
        name = ''.join(name.lower().split())
        name = name.replace('№', '').replace('#', '')
        homeworks.add(name)

    counts = []
    if homeworks:
        counts.append(len(homeworks))

    patterns = [
        r'(?:запланировано|всего)\s+(\d+)\s+домашних\s+заданий',
        r'(?:запланировано|всего)\s+домашних\s+заданий\s*[:—–-]?\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            counts.append(int(match.group(1)))
            break
    if counts:
        return max(counts)

    return None

def get_course_text(content):
    text = content.text
    toc = content.find(id='toc')

    if toc is not None:
        text = text.replace(toc.text, '', 1)

    return text

def find_field(content, section, pattern):
    for section_name, section_text in section.items():
        if (re.fullmatch(pattern + r'\s*:?', section_name, flags=re.IGNORECASE)):
            if section_text:
                return section_text.strip()

    text = get_course_text(content)
    pattern = pattern + r'[ \t]*(?:[:-]|\n)\s*([^\n]+)'
    
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
           value = match.group(1).strip()
   
           if value and value not in section:
               return value

    return None

def find_projects(content):
    text = get_course_text(content).lower()

    pattern = (
        r'(?:итогов|курсов)\w*\s+проект\w*|(?:курсов|проектн)\w*\s+работ\w*|защит\w*\s+проект\w*'
    )
    for line in text.splitlines():
        if re.search(pattern, line, flags=re.IGNORECASE) and not re.search(r'не\s+предусмотрен\w*|не\s+будет|\bнет\b', line, flags=re.IGNORECASE):
            return True
    return None


    
def create_dict_for_course_info(soup):
    content = soup.find(attrs={"class": "mw-parser-output"})
    course_info = {'title': None, 
                   'assessment': None, 
                   'has_course_plan': None, 
                   'course_leader': None, 
                   'has_contacts': None, 
                   'contacts': None, 
                   'homework_count': None,
                   'is_parsed': False,
                   'has_projects': None,
                    'sections': {}}

    title_tag = soup.find(attrs={"class": "mw-page-title-main"})
    if title_tag:
        course_info['title'] = title_tag.text.strip()
    if content is None:
        course_info['full_text'] = soup.text.strip()
        return course_info

    sections = extract_sections(content)
    course_info['sections'] = sections
    course_info['full_text'] = content.text.strip()
    course_info['is_parsed'] = True
    assessment = find_field(content, sections, r'Форма\s+(?:контроля|отч[её]тности)')

    if assessment and re.search(r'зач[её]т|экзамен', assessment, flags=re.IGNORECASE):
        course_info['assessment'] = assessment
    course_info['has_course_plan'] = sections.get('План курса', None) is not None or sections.get('Программа курса', None) is not None
    course_info['course_leader'] = find_field(content, sections, r'Руководител[ьи]\s+курса')
    course_info['contacts'] = find_contacts(content)
    course_info['has_contacts'] = bool(course_info['contacts'])
    course_info['homework_count'] = get_number_homeworks_by_counting_matches(content)
    course_info['has_projects'] = find_projects(content)
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
        course_info['semesters'] = []
        for semester_name, semester_courses in courses.items():
            if url in semester_courses:
                course_info['semesters'].append(semester_name)
        courses_info[file_path] = course_info

    with open('courses_info.json', 'w', encoding='utf-8') as f:
        json.dump(courses_info, f, ensure_ascii=False, indent=4)
    return courses_info


def count_missing_values(courses_info):
    missing_counts = {}

    for course_info in courses_info.values():
        for key in course_info:
            missing_counts[key] = 0

    for course_info in courses_info.values():
        for key in missing_counts:
            if course_info.get(key) is None:
                missing_counts[key] += 1

    total = len(courses_info)
    with open('missing_values_stats.txt', 'w', encoding='utf-8') as file:
        file.write(f'Всего курсов: {total}\n\n')
        for key, count in missing_counts.items():
            file.write(f'{key}: заполнено {total - count}, пропусков {count}\n')

    return missing_counts

courses_info = create_course_info_json()
count_missing_values(courses_info)

# with open('courses_info.json', 'r', encoding='utf-8') as f:
#     courses_info = json.load(f)
#     for file_path, course_info in courses_info.items():
#         if course_info['homework_count'] is not None:
#             print(f"{course_info['url']}: {course_info['homework_count']} домашних заданий")