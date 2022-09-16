import os
from pathvalidate import sanitize_filename

from bs4 import BeautifulSoup
import requests


def check_for_redirect(response):
    if (response.is_permanent_redirect or response.is_redirect):
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        filepath = os.path.join(folder, sanitize_filename(filename))
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as file:
            file.write(response.content)

        return filepath
    except requests.exceptions.HTTPError:
        print(f'Book with with link {url} does not exist')


if __name__ == '__main__':
    for book_id in range(1, 11):
        response = requests.get(f'https://tululu.org/b{book_id}')
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('h1').text.split('::')[0].strip()

        filepath = download_txt(f'https://tululu.org/txt.php?id={book_id}', f'{title}.txt')

        if (filepath):
            print(f'{filepath} downloaded')
