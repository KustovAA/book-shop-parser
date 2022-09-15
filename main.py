import os

import requests

def fetch_book(id):
    url = f'https://tululu.org/txt.php'
    params = {'id': id}

    response = requests.get(url, params=params)
    response.raise_for_status()

    filename = os.path.join('books', f'book_{id}.txt')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    for id in range(1, 11):
        fetch_book(id)
