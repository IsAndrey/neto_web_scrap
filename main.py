import requests
import re
from fake_http_header import FakeHttpHeader
from threading import Thread, Semaphore
from bs4 import BeautifulSoup
from datetime import datetime as dt


KEYWORDS = ['data scrap', 'postgres', 'web', 'python']
KEYWORDS = ['data scrap']
WEB_PORTAL = r'https://habr.com'
MAX_PAGES = 50
DOWNLOAD_FOLDER = 'pages'
RE_COMPILE = re.compile('|'.join(KEYWORDS), re.IGNORECASE)
SEMAPHORE_10 = Semaphore(10)


def get_endpoint(page_number=1):
    if page_number == 1 or page_number > MAX_PAGES:
        return r'https://habr.com/ru/articles/page01'
    endpoint = r'/ru/articles/page' + '{:02}'.format(page_number) + r'/'
    return WEB_PORTAL + endpoint


def article_is_found(preview, full_text=''):
    if len(KEYWORDS) == 0:
        return True
    text_to_search = preview
    if full_text != '':
        text_to_search = full_text
    return RE_COMPILE.search(text_to_search) is not None


def extract_text(tag):
    if tag.sting is not None:
        return str(tag.string)
    result = ''
    for s in tag.stripped_strings:
        result += s
    return result

def get_web_page(url):
    headers = FakeHttpHeader().as_header_dict()
    response = requests.get(url=WEB_PORTAL, headers=headers)
    with open('headers.txt', 'w', encoding='utf-8') as h:
        h.write(str(headers))
    if response.status_code == 200:
        return response.text
    return None

def get_formatted_body(tag):
    return (
        tag.find(
            name='div',
            class_='article-formatted-body article-formatted-body article-formatted-body_version-1'
        ),
        tag.find(
            name='div',
            class_='article-formatted-body article-formatted-body article-formatted-body_version-2'
        )
    )

'''
with open('habr.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'lxml')
    with open('soup.html', 'w', encoding='utf-8') as s:
        s.write(soup.prettify())
'''

def main(page_number=1):
    # SEMAPHORE_10.acquire()
    print(get_endpoint(page_number))
    web_page = get_web_page(get_endpoint(page_number))
    if web_page is None:
        return
    with open('habr.html', 'w', encoding='utf-8') as f:
        f.write(web_page)
    html = BeautifulSoup(web_page, 'lxml')
    articles = html.find_all(name='article', class_='tm-articles-list__item')
    print(len(articles))
    for article in articles:
        # Время публикации
        article_time = article.find(name='time')
        if article_time is None:
            continue
        date = dt.fromisoformat(article_time['datetime'][:-5]).date()
        # Название статьи и ссылка
        article_title = article.find(name='a', class_='tm-title__link')
        if article_title is None:
            continue
        href = WEB_PORTAL+article_title['href']
        title = article_title.span.string
        # Текст превью используются 2 формата
        article_preview_v1, article_preview_v2 = get_formatted_body(article)

        preview = ''
        if article_preview_v1 is not None:
            preview = extract_text(article_preview_v1)
        elif article_preview_v2 is not None:
            preview = extract_text(article_preview_v2)

        body = ''
        article_source = get_web_page(href)
        if article_source is not None:
            html = BeautifulSoup(article_source, 'lxml')
            if html is not None:
                article_preview_v1, article_preview_v2 = get_formatted_body(html)
                if article_preview_v1 is not None:
                    body = extract_text(article_preview_v1)
                elif article_preview_v2 is not None:
                    body = extract_text(article_preview_v2)

        if article_is_found(preview, body):
            print(date, title, href, sep=' - ')
        else:
            print(date, title, href, sep=' / ')
    # SEMAPHORE_10.release()


if __name__=='__main__':
    '''
    threads = [Thread(target=main, args=(i,)) for i in range(1, 2)]
    for t in threads:
        t.start()

    for t in threads:
        t.join()
    '''
    main(50)
