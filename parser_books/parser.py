import asyncio
import os
import re
import sys

from aiohttp import ClientSession
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup

from parser_books.serializers import BookCreateSerializer

__url = 'https://litrpg.ru'
books_data = []


def run_parser(all=True, first_page=1, last_page=1):
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }

    if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(gather_data(HEADERS, first_page, last_page, all, 30))

    print(f'Всего книг: {len(books_data)}')
    data = [book["title"] for book in books_data]
    data.sort()
    [print(f'{idx + 1:<5}{book}') for idx, book in enumerate(data)]
    print()


async def get_last_page(session: ClientSession, headers: dict) -> int:
    """
    Возвращает номер последней страницы

    :param session:
    :param headers:
    :return : Номер последней страницы
    """

    url = 'https://litrpg.ru/index.php?section=find&p=on'
    repeat = 5

    # Пробует запустить страницу repeat раз
    for _ in range(repeat):
        response = await session.get(url=url, headers=headers)
        if response.status != 200:
            continue
        soup = BeautifulSoup(await response.text(), 'lxml')
        return int(
            soup.find('div', class_='paginator').find_all('span')[-1].text
        )
    return 0


async def gather_data(
        headers: dict, first_page: int, last_page: int, all: bool, step: int
):
    """
    Запускает обработку страаниц с книгами

    :param headers:
    :param first_page: Номер первой страницы
    :param last_page: Номер последней страницы
    :param all: Нужено использовать все страницы
    :param step: По сколько страниц будет приходится на один поток
    :return:
    """

    async with ClientSession() as session:
        if all:
            first_page = 1
            last_page = await get_last_page(session, headers)
        if last_page:
            await parser_pages(session, headers, first_page, last_page, step)
        else:
            print(f'Невозможно запустить парсер. \nПричина: {last_page = }')


async def parser_pages(
        session: ClientSession, headers: dict, first_page: int, last_page: int, step: int
):
    """
    Формирует для сборки пакеты страниц парсера

    :param session: ClientSession
    :param headers: dict
    :param first_page:
    :param last_page:
    :param step:
    :return:
    """

    while first_page + step <= last_page:
        await tasks_pages(session, headers, first_page, first_page + step)
        first_page += step

    await tasks_pages(session, headers, first_page, last_page + 1)


async def tasks_pages(
        session: ClientSession, headers: dict, first_page: int, last_page: int
):
    """
    Собирает пакеты страниц парсера

    :param session: ClientSession
    :param headers: dict
    :param first_page: int - Номер первой страницы
    :param last_page: int - Номер последней страницы
    :return:
    """

    tasks = []

    for num in range(first_page, last_page):

        task = asyncio.create_task(get_page_data(session, headers, num))
        tasks.append(task)

    await asyncio.gather(*tasks)


async def get_page_data(session: ClientSession, headers: dict, page: int) -> None:
    # Запускает обработку книг, находящихся на данной странице

    url = f'{__url}/index.php?section=find&page={page}'
    async with session.get(url=url, headers=headers, ) as response:
        tasks = []
        soup = BeautifulSoup(await response.text(), 'lxml').find_all(class_='FicTbl')
        for book in soup:
            book_url = book.find(class_='FicTable_Title').find('a').attrs['href']
            task = asyncio.create_task(get_book(session, headers, f'{__url}{book_url}', page))
            tasks.append(task)
            # break
            # ToDo

        await asyncio.gather(*tasks, return_exceptions=False)
        # books_data.extend([data.result() for data in tasks if isinstance(data.result(), dict)])

        if False:

            for data in tasks:
                if isinstance(data.result(), dict):
                    await save_to_db(data.result())
        else:
            books_data.extend(
                [data.result() for data in tasks if isinstance(data.result(), dict)])


@sync_to_async
def save_to_db(data: dict) -> None:
    try:
        serializer = BookCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        q = serializer.save()
        # print(serializer.data)
    except:
        ...


async def get_book(session, headers, url, page, level=5):
    #  Получает данные о книге и возвращает их

    async with session.get(url=url, headers=headers) as response:
        if response.status != 200:
            print(f'Error {level = }: page - {page:3}, url - {url} status - {response.status}')
            if level:
                return asyncio.create_task(get_book(session, headers, url, page, level=level - 1))
        else:
            try:
                text = await response.text(encoding='latin-1')
                soup = BeautifulSoup(text.encode('latin-1').decode('utf-8', 'ignore'), 'lxml')
                data = {
                    'title': soup.find(class_='ContentTable').find('h1').text,
                    'description': soup.find(class_='summary_text_fic3').text,
                    'status': None,
                    'genres_name': None,
                    'series_name': None,
                    'authors_name': None,
                    'dates': None,
                }

                data_info = [
                    {
                        'name': 'dates',
                        'string': ['Даты:'],
                        're': r'([\d.]+)',
                        'list': True
                    }, {
                        'name': 'authors_name',
                        'string': ['Автор:', 'Авторы:'],
                        're': r'\s((?!Автор)[\wа-яА-Я][\wа-яА-Я ]+)',
                        'list': True
                    }, {
                        'name': 'genres_name',
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
                        info = soup.find(class_='FicHead')\
                            .find(class_='title', string=sub_data['string']).parent.text
                        data[sub_data['name']] = re.findall(sub_data['re'], info) \
                            if sub_data['list'] \
                            else re.findall(sub_data['re'], info)[0]
                    except:
                        pass

                data['image_url'] = await download_img(
                    session,
                    headers,
                    soup,
                    re.sub(r'[^\d\wа-яА-Я\.\- ]+', '', data['title'])
                )

            except Exception as exp:
                print(f'Error: page - {page}, url - {url} -> '
                      f'{exp}, status - {response.status}')
            return data


async def download_img(session, headers, soup, title='NoNameBook'):
    # Сохраняет изображение и возвращает путь к нему

    path_to_save = 'images/'
    try:
        img_url = soup.find(class_='open-picture').attrs['src']
        url = __url + '-big'.join(re.findall(r'^(\S+)(\.\S+)$', img_url)[0])
        file_name = f'{path_to_save}{title}_{url.split("/")[-1]}'
        if os.path.exists(file_name):
            return file_name

        async with session.get(url=url, headers=headers) as response:
            # Сохранение изображения
            with open(f'./files/{file_name}', 'wb') as image:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    image.write(chunk)

            return file_name

    except Exception as exp:
        # print(exp)
        ...
