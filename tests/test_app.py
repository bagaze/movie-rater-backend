from app import __version__
from app.schemas.movie import MovieResult
from app.proxy import tmdb_api
import pytest

pytest_plugins = ('pytest_asyncio',)


def test_version():
    assert __version__ == '0.1.0'


def test_movie_results():
    movie_result_obj = {
        'page': 1,
        'total_results': 1,
        'total_pages': 1,
        'results': [
            {
                'id': 1,
                'imdb_id': 'tt1234567',
                'original_title': 'original title',
                'title': 'title',
                'release_date': '2022-04-13',
                'directors': ['director 1', 'director 2'],
                'vote_average': 10.0,
                'vote_count': 1
            }
        ]
    }

    movie_result = MovieResult(**movie_result_obj)

    assert movie_result.results[0].id == movie_result_obj['results'][0]['id']


@pytest.mark.asyncio
async def test_tmdb_discover_movies():
    (status, resp) = await tmdb_api.get_discover_movies(
        {
            'primary_release_date.gte': '2022-04-01',
            'primary_release_date.lte': '2022-04-05'
        }
    )
    assert status == 200
    assert resp['page'] == 1
    assert resp['total_results'] == 5
