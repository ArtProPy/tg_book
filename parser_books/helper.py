import asyncio
import datetime
import os
import re
import sys

import aiohttp
import requests
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup

from parser_books.serializers import BookCreateSerializer, AsyncBookCreateSerializer


class Parser:
    def __init__(self, url, all_page=False, from_page=1, to_page=1):
        self.url = url
        self.all = all_page
        self.from_page = from_page
        self.to_page = to_page

    def get_book(self, url):
        soup = self.soup(url)
        return {'title': soup.find(class_='ContentTable').find('h1').text}

    @staticmethod
    def soup(url):
        return BeautifulSoup(requests.get(url).text, 'lxml')

    def get_books_data(self):
        data = []
        if self.all:
            pass
        for page in range(self.from_page, self.to_page + 1):
            url = f'{self.url}index.php?section=find&page={page}'
            data.extend(self.get_data_page(url))
        return data

    def get_data_page(self, url):
        books_data = []
        for book in self.soup(url).find_all(class_='FicTbl'):
            book_url = book.find(class_='FicTable_Title').find('a').attrs['href']
            books_data.append(self.get_book(f'{self.url}{book_url}'))
        return books_data


class ParserAsync:
    books_data = []
    __headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }
    __url = 'https://litrpg.ru'

    def __init__(self, step=30):
        self.step = step

    async def parser_pages(self, session, headers, from_page=1, to_page=1):
        tasks = []
        for num in range(from_page, to_page):
            task = asyncio.create_task(self.get_page_data(session, headers, num))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def gather_data(self, step, headers, all, page, last_page):
        # Запускает обработку страаниц с книгами

        url = 'https://litrpg.ru/index.php?section=find&p=on'
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), 'lxml')
            if all:
                page = 1
                last_page = int(
                    soup.find('div', class_='paginator').find_all('span')[-1].text
                )

            while page + step <= last_page:
                await self.parser_pages(session, headers, page, page + step)
                page += step

            await self.parser_pages(session, headers, page, last_page + 1)

    async def get_page_data(self, session, headers, page):
        # Запускает обработку книг, находящихся на данной странице

        url = f'{self.__url}/index.php?section=find&page={page}'
        async with session.get(url=url, headers=headers) as response:
            tasks = []
            soup = BeautifulSoup(await response.text(), 'lxml').find_all(class_='FicTbl')
            for book in soup:
                book_url = book.find(class_='FicTable_Title').find('a').attrs['href']
                task = asyncio.create_task(self.get_book(session, headers, f'{self.__url}{book_url}', page))
                tasks.append(task)
                # break
                # ToDo

            await asyncio.gather(*tasks, return_exceptions=False)
            self.books_data.extend([data.result() for data in tasks if isinstance(data.result(), dict)])

            if True:

                for data in tasks:
                    if isinstance(data.result(), dict):
                        await qs(data.result())

            # print(tasks)

    async def get_book(self, session, headers, url, page, level=5):
        #  Получает данные о книге и возвращает их

        async with session.get(url=url, headers=headers) as response:
            if response.status != 200:
                print(f'Error {level = }: page - {page:3}, url - {url} status - {response.status}')
                if level:
                    return asyncio.create_task(self.get_book(session, headers, url, page, level=level - 1))
            else:
                try:
                    text = await response.text(encoding='latin-1')
                    soup = BeautifulSoup(text.encode('latin-1').decode('utf-8', 'ignore'), 'lxml')
                    data = {
                        'title': soup.find(class_='ContentTable').find('h1').text,
                        'description': soup.find(class_='summary_text_fic3').text,
                        'status': None,
                        'genres': None,
                        'series_name': None,
                        'authors': None,
                        'dates': None,
                    }

                    data_info = [
                        {
                            'name': 'dates',
                            'string': ['Даты:'],
                            're': r'([\d.]+)',
                            'list': True
                        }, {
                            'name': 'authors',
                            'string': ['Автор:', 'Авторы:'],
                            're': r'\s((?!Автор)[\wа-яА-Я][\wа-яА-Я ]+)',
                            'list': True
                        }, {
                            'name': 'genres',
                            'string': ['Жанр:'],
                            're': r'\s((?!Жанр)[\wа-яА-Я][\wа-яА-Я ]+)',
                            'list': True
                        }, {
                            'name': 'series_name',
                            'string': ['Серия:'],
                            're': r'\s((?!Серия)[\wа-яА-Я][\wа-яА-Я ]+)',
                            'list': False
                        }, {
                            'name': 'status',
                            'string': ['Статус:'],
                            're': r'\s((?!Статус)[\wа-яА-Я][\wа-яА-Я ]+)',
                            'list': False
                        }
                    ]

                    for sub_data in data_info:
                        try:
                            info = soup.find(class_='FicHead').find(class_='title', string=sub_data['string']).parent.text
                            data[sub_data['name']] = re.findall(sub_data['re'], info) \
                                if sub_data['list'] \
                                else re.findall(sub_data['re'], info)[0]
                        except:
                            pass

                    data['image_url'] = await self.download_img(
                        session, headers, soup, re.sub(r'[^\d\wа-яА-Я\.\- ]+', '', data['title'])
                    )

                except Exception as exp:
                    print(f'Error: page - {page}, url - {url} -> {exp}, status - {response.status}')
                return data

    async def download_img(self, session, headers, soup, title='NoNameBook'):
        # Сохраняет изображение и возвращает путь к нему

        path_to_save = 'images/'
        try:
            img_url = soup.find(class_='open-picture').attrs['src']
            url = self.__url + '-big'.join(re.findall(r'^(\S+)(\.\S+)$', img_url)[0])
            file_name = f'{path_to_save}{title}_{url.split("/")[-1]}'
            if os.path.exists(file_name):
                return file_name

            async with session.get(url=url, headers=headers) as response:
                # Сохранение изображения
                with open(f'./files/{file_name}', 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

                return file_name

        except Exception as exp:
            # print(exp)
            ...

    def run(self, all=True, page=1, last_page=1):
        self.books_data = []
        if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.gather_data(self.step, self.__headers, all, page, last_page))

        # print(f'Всего книг: {len(self.books_data)}')
        # [print(f'{idx + 1:<5}{book["title"]}') for idx, book in enumerate(self.books_data)]
        # print()


if __name__ == '__main__':
    with open('data.txt', 'w') as file:
        for step in [20]:
            file.write(f'{step = }\t')
            times = []
            for _ in range(1):
                # print()
                # print('=' * 100)
                # print(f'step = {step}')
                s_time = datetime.datetime.now()
                parser = ParserAsync(step=step)
                parser.run(all=False, last_page=5)
                times.append(datetime.datetime.now() - s_time)
                [print(f'{idx + 1}: {time}') for idx, time in enumerate(times)]

                file.write(str(times[-1]))
                file.write('\n')
                # print(times[-1])
                # print('=' * 100)
            file.write('\n')
            print()
            # print(sum(times) / len(times))


@sync_to_async
def qs(data):
    try:
        serializer = BookCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        q = serializer.save()
        # print(serializer.data)
    except:
        ...
