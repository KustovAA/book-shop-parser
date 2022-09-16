from argparse import ArgumentParser
from urllib.parse import urljoin, unquote, urlencode
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
from retry import retry


def check_for_redirect(response):
    if (response.is_permanent_redirect or response.is_redirect):
        raise requests.exceptions.HTTPError


@retry(exceptions=requests.exceptions.ConnectionError, delay=1, backoff=2, tries=10)
def download_file(
    url,
    filename,
    folder,
    get_content=lambda r: r.content,
    mode='wb'
):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    check_for_redirect(response)
    filepath = os.path.join(folder, sanitize_filename(filename))

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode) as file:
        file.write(get_content(response))

    return filepath


def download_txt(url, filename, folder='books/'):
    return download_file(
        url,
        filename,
        folder,
        get_content=lambda r: r.text,
        mode='w'
    )


def download_image(url, filename, folder='images/'):
    return download_file(url, filename, folder)


def parse_book_page(page):
    soup = BeautifulSoup(page, 'lxml')
    title, author = [item.strip() for item in soup.find('h1').text.split('::')]
    comments = [comment.text for comment in soup.select('.texts .black')]
    genres = [genre.text for genre in soup.select_one('.d_book:-soup-contains("Жанр книги:")').find_all('a')]
    img = soup.find(class_='bookimage').find('img').attrs.get('src')

    return {
        'title': title,
        'author': author,
        'comments': comments,
        'genres': genres,
        'img': img
    }


if __name__ == '__main__':
        parser = ArgumentParser(description='Utility downloads books (book text in txt file, and cover) from tululu.org')
        parser.add_argument('--start_id', type=int, default=1, help="id of first book in sequence")
        parser.add_argument('--end_id', type=int, default=11, help="id of last book in sequence")
        args = parser.parse_args()
        start_id = args.start_id
        end_id = args.end_id

        for book_id in range(start_id, end_id):
            try:
                url = f'https://tululu.org/b{book_id}/'
                response = requests.get(url, allow_redirects=False)
                check_for_redirect(response)
                book = parse_book_page(response.text)
                title = book['title']
                img = book['img']

                img_url = urljoin(urljoin(url, '..'), img)

                params = {'id': book_id}
                book_filepath = download_txt(f'https://tululu.org/txt.php?{urlencode(params)}', f'{book_id}. {title}.txt')
                img_filepath = download_image(img_url, unquote(img).split('/')[-1])

                if book_filepath:
                    print(f'{book_filepath} downloaded')

                if img_filepath:
                    print(f'{img_filepath} downloaded')
            except requests.exceptions.HTTPError:
                print(f'Book with with link {url} does not exist')
