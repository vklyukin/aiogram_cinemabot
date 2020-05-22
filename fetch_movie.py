import asyncio
import random
import typing as tp
from aiohttp import ClientSession
from bs4 import BeautifulSoup


headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/79.0.3945.130 '
                         'Safari/537.36'
           }
GOOGLE_URL_SEARCH = 'https://www.google.ru/search'
IMDB_URL_SEARCH = 'https://www.imdb.com/chart/top'
IMDB_BASE_URL = 'https://www.imdb.com/'


async def fetch_movie(loop: asyncio.AbstractEventLoop, movie_name: str) -> tp.Optional[tp.Tuple[str, str]]:
    """
    Asynchronous function to find the link forwarding to the website where user could watch film
    :param loop: event_loop
    :param movie_name: user's query
    :return: tuple of title of the link and the link itself (or None)
    """
    async with ClientSession(loop=loop) as session:
        async with session.get(GOOGLE_URL_SEARCH, params={'q': f'{movie_name} смотреть'}, headers=headers) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            page = soup.find_all('div', attrs={'class': 'g'})
            for div in page:
                try:
                    title = div.find('h3').get_text()
                    link = div.find('a', href=True)
                    if title and link:
                        return title, link['href']
                except AttributeError or RuntimeError:
                    continue


async def imdb_random_from_top(loop: asyncio.AbstractEventLoop) -> tp.Optional[tp.Tuple[str, str, float]]:
    """
    Asynchronous function to pick the movie from the IMDb top-250 randomly
    :param loop: event_loop
    :return: tuple of title of the movie and the link to it and rating (or None)
    """
    async with ClientSession(loop=loop) as session:
        async with session.get(IMDB_URL_SEARCH, headers=headers) as response:
            try:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                page = soup.find_all('tr')

                selected_movie_id = random.randint(0, len(page) - 1)
                selected_movie = page[selected_movie_id].find('td', attrs={'class': 'titleColumn'}).find('a', href=True)

                title = selected_movie.get_text()
                link = IMDB_BASE_URL + selected_movie['href']
                rating = float(page[selected_movie_id].find('td', attrs={'class': 'ratingColumn imdbRating'})
                               .find('strong')
                               .get_text())
                return title, link, rating
            except AttributeError:
                return None
