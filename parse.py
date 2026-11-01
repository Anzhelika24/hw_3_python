from bs4 import BeautifulSoup

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
with open('python_course.txt', 'w', encoding='utf-8') as f:
    # f.write(soup.find('h1').text + '\n')
    f.write(soup.find(attrs={'class': 'mw-parser-output'}).text)
