import os

import requests

def check_for_redirect(response):
    if (response.is_permanent_redirect or response.is_redirect):
        raise requests.exceptions.HTTPError


def fetch_book(id):
    url = f'https://tululu.org/txt.php'
    params = {'id': id}

    response = requests.get(url, params=params, allow_redirects=False)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        filename = os.path.join('books', f'book_{id}.txt')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.HTTPError:
        print(f'Book with id {id} does not exist')


if __name__ == '__main__':
    for id in range(1, 11):
        fetch_book(id)
