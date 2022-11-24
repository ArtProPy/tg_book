import json
import re

import aiohttp
import requests

from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(requests.get(url).text, 'lxml')
        self.cards = {'class_': 'FicTbl'}
        self.card_fields = {}

    def get_last_book_path(self):
        return self.soup.find(class_='FicTable_Title').find('a').attrs['href']

    def gen_url_books(self):
        for idx in range(
                int(re.findall('\d+$', self.get_last_book_path())[0]), 1, -1
        ):
            yield f'{self.url}/book{idx}'

    def get_book(self, url):
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        book = {
            'num_book': int(re.findall('\d+$', url)[0]),
            'title': soup.find(class_='ContentTable').find('h1').text,
            'img_src': soup.find(class_='open-picture').attrs[
                'data-src'] if soup.find(class_='open-picture') else None,
            'description': soup.find(class_='summary_text_fic3').text,
            'authors': self.get_authors(soup.find(class_='FicHeadRight')),
            'genres': self.get_genres(soup.find(class_='FicHeadRight')),
            'size': 'Неизвестно',
            'status': 'Неизвестно',
        }
        return book

    @staticmethod
    def get_list_field(field_soup):
        pattern = ' ([a-zA-Zа-яА-Я .]+)'
        if field_soup:
            return re.findall(
                pattern, field_soup.parent.text.replace('\n', ' ').strip()
            )
        return []

    def get_authors(self, soup):
        authors = soup.find(class_='title', string='Автор:') \
            if soup.find(class_='title', string='Автор:') \
            else soup.find(class_='title', string='Авторы:')
        return self.get_list_field(authors)

    def get_genres(self, soup):
        genres = soup.find(class_='title', string='Жанр:')
        return self.get_list_field(genres)

    def update_all_books(self):
        num_book = 1
        for url in self.gen_url_books():
            if num_book == 2:
                break
            self.get_book(url)
            num_book += 1

    def get_books(self, url):
        books_data = []
        for book in self.soup.find_all(**self.cards):
            book_data = {
                'title': book.find(class_='FicTable_Title').find('a').text,
                'img_src': book.find(class_='open-picture').attrs[
                    'src'] if book.find(class_='open-picture') else None,
                'description': book.find(class_='FicTbl_sammary').text,
                'authors': [],
                'genres': [],
                'size': 'Неизвестно',
                'status': 'Неизвестно',
            }
            q = [x for x in book.find(class_='FicTbl_meta').children if
                 x.text.replace(',', '').strip()]
            fields = {
                'Автор:': 'authors',
                'Авторы:': 'authors',
                'Жанры:': 'genres',
                'Серия:': 'series',
                'Размер:': 'size',
                'Статус:': 'status',
            }
            field = ''
            for x in q:
                if x.name == 'b':
                    field = fields.get(x.text, None)
                    continue
                text = x.text.strip()
                if field == 'authors':
                    book_data[field].append(text)
                elif field == 'genres':
                    book_data[field] = text.split(', ')
                elif field is None:
                    continue
                else:
                    book_data[field] = text
            books_data.append(book_data)

        return books_data




if __name__ == '__main__':
    url = 'https://litrpg.ru/index.php?section=find&page=1'
    parser = Parser(url)
    print(parser.update_all_books())
    with open('books.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(parser.get_books(url), indent=2, ensure_ascii=False))
