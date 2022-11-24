import asyncio
import datetime
import sys
import time

import aiohttp
import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url, all_page=False, from_page=1, to_page=1):
        self.url = url
        self.all = all_page
        self.from_page = from_page
        self.to_page = to_page
        # self.soup = BeautifulSoup(requests.get(url).text, 'lxml')

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
        for page in range(self.from_page, self.to_page+1):
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
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }
    url = 'https://litrpg.ru'

    def __init__(self, step=30):
        self.step = step

    async def parser_pages(self, session, headers, from_page=1, to_page=1):
        tasks = []
        for num in range(from_page, to_page):
            task = asyncio.create_task(self.get_page_data(session, headers, num))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def gather_data(self, step, headers):
        url = 'https://litrpg.ru/index.php?section=find&p=on'
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), 'lxml')
            last_page = int(soup.find('div', class_='paginator').find_all('span')[-1].text)
            last_page = 20
            page = 1

            while page + step <= last_page:
                await self.parser_pages(session, headers, page, page+step)
                page += step
                # print(f'{"-"*20}NEXT {page}-{page + self.step}|{"-"*20}')
            await self.parser_pages(session, headers, page, last_page+1)

    async def get_page_data(self, session, headers, page):
        url = f'{self.url}/index.php?section=find&page={page}'
        async with session.get(url=url, headers=headers) as response:
            tasks = []
            soup = BeautifulSoup(await response.text(), 'lxml').find_all(class_='FicTbl')
            for book in soup:
                book_url = book.find(class_='FicTable_Title').find('a').attrs['href']
                task = asyncio.create_task(self.get_book(session, headers, f'{self.url}{book_url}', page))
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=False)
        # print(f'{page: 003}:Finish: get_page_data')

    async def get_book(self, session, headers, url, page):
        async with session.get(url=url, headers=headers) as response:
            book_received = False
            for _ in range(5):
                try:
                    soup = BeautifulSoup(await response.text(encoding='latin-1'), 'lxml')
                    data = {
                        'title': soup.find(class_='ContentTable').find('h1').text.encode('latin-1').decode('utf8'),
                        'description': soup.find(class_='summary_text_fic3').text.encode('latin-1').decode('utf8'),
                    }
                    self.books_data.append(data)
                    if book_received:
                        break
                except Exception as exp:
                    print(f'Error: page - {page}, url - {url} -> {exp}')

    def run(self):
        self.books_data = []
        if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.gather_data(self.step, self.headers))

        print(f'Всего книг: {len(self.books_data)}')
        print(self.books_data)
        print()


if __name__ == '__main__':
    with open('data.txt', 'w') as file:
        for step in [5, 10, 50]:
            file.write(f'{step = }/n')
            times = []
            for _ in range(10):
                # print()
                # print('=' * 100)
                # print(f'step = {step}')
                s_time = datetime.datetime.now()
                parser = ParserAsync(step=step)
                parser.run()
                times.append(datetime.datetime.now() - s_time)
                file.write(str(times[-1]))
                file.write('\n')
                # print(times[-1])
                # print('=' * 100)
            file.write('\n')
            print()
            [print(f'{idx+1}: {time}') for idx, time in enumerate(times)]
            # print(sum(times) / len(times))
