from argparse import ArgumentParser
from urllib.parse import urljoin, unquote
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


def check_for_redirect(response):
    if (response.is_permanent_redirect or response.is_redirect):
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    check_for_redirect(response)
    filepath = os.path.join(folder, sanitize_filename(filename))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_image(url, filename, folder='images/'):
    return download_txt(url, filename, folder)


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
        parser = ArgumentParser()
        parser.add_argument('--start_id', default=1)
        parser.add_argument('--end_id', default=11)
        args = parser.parse_args()
        start_id = int(args.start_id)
        end_id = int(args.end_id)

        for book_id in range(start_id, end_id):
            try:
                url = f'https://tululu.org/b{book_id}/'
                response = requests.get(url, allow_redirects=False)
                check_for_redirect(response)
                book_info = parse_book_page(response.text)
                title = book_info['title']
                img = book_info['img']
                

                img_url = urljoin('https://tululu.org', img)

                book_filepath = download_txt(f'https://tululu.org/txt.php?id={book_id}', f'{book_id}. {title}.txt')
                img_filepath = download_image(img_url, unquote(img).split('/')[-1])

                if (book_filepath):
                    print(f'{book_filepath} downloaded')

                if (img_filepath):
                    print(f'{img_filepath} downloaded')
            except requests.exceptions.HTTPError:
                print(f'Book with with link {url} does not exist')
