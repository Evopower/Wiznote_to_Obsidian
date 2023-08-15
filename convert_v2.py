import html2text
import os
import re
from bs4 import BeautifulSoup
import shutil

def table_to_markdown(table):
    markdown_table = []
    rows = table.find_all('tr')
    for row in rows:
        markdown_row = []
        columns = row.find_all(['td', 'th'])
        for column in columns:
            markdown_row.append(column.get_text().strip())
        markdown_table.append(' | '.join(markdown_row))
    return '\n'.join(markdown_table)
def html_to_markdown(html_file, md_file, source_directory, target_directory):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 处理代码块
    code_blocks = soup.find_all('div', class_='wiz-code-container')
    for block in code_blocks:
        code = block.find('textarea').string
        language = block.get('data-mode', '')
        block.replace_with(f'```{language}\n{code}\n```')

    # 处理图片
    image_tags = soup.find_all('img')
    for img in image_tags:
        src = img.get('src', '')
        alt = img.get('alt', '')
        img.replace_with(f'![{alt}]({src})')

        # 复制图片文件
        source_img_file = os.path.join(os.path.dirname(html_file), src)
        target_img_file = os.path.join(target_directory, os.path.relpath(source_img_file, source_directory))

        # 创建目标图片文件夹
        os.makedirs(os.path.dirname(target_img_file), exist_ok=True)
        shutil.copyfile(source_img_file, target_img_file)

        # 处理表格
    tables = soup.find_all('table')
    for table in tables:
        markdown_table = table_to_markdown(table)
        table.replace_with(markdown_table)

    html_content = str(soup)
    markdown_content = html2text.html2text(html_content)

    # 修复 ```language code``` 为 ```language\n code\n\n```
    # 处理多行代码的情况
    markdown_content = re.sub(r'(```\w+)(\s*)(.*?)```', r'\1\n\3\n```\n', markdown_content, flags=re.DOTALL)

    # 确保目录存在，如果不存在，创建目录
    os.makedirs(os.path.dirname(md_file), exist_ok=True)

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)


source_directory = './Wiznote'
# 输入你的目标文件夹路径
target_directory = './科研'

for dirpath, dirnames, filenames in os.walk(source_directory):
    for filename in filenames:
        if filename.endswith('.html'):
            html_file = os.path.join(dirpath, filename)
            # 构造新的目标文件路径，保持原来的目录结构
            relative_path = os.path.relpath(dirpath, source_directory)
            md_file = os.path.join(target_directory, relative_path, filename[:-5] + '.md')
            html_to_markdown(html_file, md_file, source_directory, target_directory)
