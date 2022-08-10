import requests
from bs4 import BeautifulSoup


def API(movieName):
    url = f"https://omdbapi.com/?t={movieName}&apikey=APIKEY"  ## get your own API key at https://omdbapi.com/
    res = requests.get(url)

    data = res.json()

    try:
        imdb_id = data["imdbID"]
    except:
        imdb_id = "tt0499549"
    return imdb_id


def movie_trivia(mid):
    url = f'https://www.imdb.com/title/{mid}/trivia'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    trivia_text = soup.select('.sodatext')

    trivia = []
    for text in trivia_text:
        text = text.get_text()
        text = text.strip().replace('\n', "")
        trivia.append(text)
        if len(trivia) > 7:  ## extracting only 7
            break
    return trivia


movie_name = input('Movie Name....\n')
id = API(movie_name)
trivia_list = movie_trivia(id)
for trivia in trivia_list:
    print(trivia, end='\n')
