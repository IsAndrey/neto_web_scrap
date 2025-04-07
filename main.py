from os.path import isfile
import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt


KEYWORDS = ['дизайн', 'фото', 'web', 'python']
WEB_PORTAL = 'https://habr.com/ru/articles/'
PAGES = 50


'''
response = requests.get(url=WEB_PORTAL)
if response.status_code == 200:
    with open('habr.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
'''
with open('habr.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'lxml')
    with open('soup.html', 'w', encoding='utf-8') as s:
        s.write(soup.prettify())

articles = soup.find_all(name='article', class_='tm-articles-list__item')
print(len(articles))
for article in articles:
    article_date = article.find(name='time')
    article_title = article.find(name='a', class_='tm-title__link')
    href = WEB_PORTAL[:-1]+article_title['href']
    title = article_title.span.string
    date = dt.fromisoformat(article_date['datetime'][:-5]).date()
    article_body = article.find(
        name='div',
        class_='article-formatted-body article-formatted-body article-formatted-body_version-2')
    body = ''
    if article_body is not None:
        body_parts = article_body.find_all(name='p')
        for part in body_parts:
            if part.string is not None:
                body += part.string
    print(date, title, href, sep=' - ')
    print(body[:200])