import requests
import re
from fake_http_header import FakeHttpHeader
from threading import Thread, Semaphore
from bs4 import BeautifulSoup
from datetime import datetime as dt


KEYWORDS = ['фото', 'дизайн', 'web', 'python']
WEB_PORTAL = r'https://habr.com'
MAX_PAGES = 50
RE_COMPILE = re.compile('|'.join(KEYWORDS), re.IGNORECASE)
SEMAPHORE_10 = Semaphore(10)  # Запустим одновременно 10 потоков для скраппинга
count_articles = 0


def get_endpoint(page_number=1):
    """Получает эндпоинт по номеру страницы."""
    if page_number == 1 or page_number > MAX_PAGES:
        return r'https://habr.com/ru/articles/'
    endpoint = r'/ru/articles/page' + '{:02}'.format(page_number) + r'/'
    return WEB_PORTAL + endpoint


def article_is_found(preview, full_text=''):
    """Проверяет наличие в тексте ключевых слов."""
    if len(KEYWORDS) == 0:
        return True
    text_to_search = preview
    if full_text != '':
        text_to_search = full_text
    return RE_COMPILE.search(text_to_search) is not None


def extract_text(tag):
    """Получает текст из тэга."""
    if tag.sting is not None:
        return tag.string
    result = ''
    for s in tag.stripped_strings:
        result += s
    return result


def get_web_page(url):
    """Получает текст вэб страницы."""
    headers = FakeHttpHeader().as_header_dict()
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def get_formatted_body(tag):
    """Поиск тэга со статьей."""
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


def main(page_number=1):
    """Скраппинг."""
    SEMAPHORE_10.acquire()

    global count_articles
    web_page = get_web_page(get_endpoint(page_number))
    if web_page is None:
        return
    html = BeautifulSoup(web_page, 'lxml')
    if html is None:
        return
    articles = html.find_all(name='article', class_='tm-articles-list__item')
    if articles is None:
        return

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
        title = extract_text(article_title.span)
        # Текст превью
        preview = ''
        article_preview_v1, article_preview_v2 = get_formatted_body(article)     
        if article_preview_v1 is not None:
            preview = extract_text(article_preview_v1)
        elif article_preview_v2 is not None:
            preview = extract_text(article_preview_v2)
        # Полный текст статьи
        body = ''
        article_source = get_web_page(href)
        if article_source is not None:
            html = BeautifulSoup(article_source, 'lxml')
            if html is not None:
                article_body_v1, article_body_v2 = get_formatted_body(html)
                if article_body_v1 is not None:
                    body = extract_text(article_body_v1)
                elif article_body_v2 is not None:
                    body = extract_text(article_body_v2)

        if article_is_found(preview, body):
            # Дополнительно к ТЗ выводится номер страницы, на которой найдена статья
            print(date, title, href, f'страница {page_number}', sep=' - ')
            count_articles += 1

    SEMAPHORE_10.release()


if __name__=='__main__':
    threads = [Thread(target=main, args=(i,)) for i in range(1, MAX_PAGES+1)]
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print(f'ВСЕГО найдено {count_articles} статей, содержащих ключевые слова {', '.join(KEYWORDS)}.')
