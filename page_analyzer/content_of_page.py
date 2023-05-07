from bs4 import BeautifulSoup4


def get_content(content):
    soup = BeautifulSoup(content, 'lxml')
    h1 = soup.find('h1').get_text() if soup.find('h1') else ''
    title = soup.find('title').get_text() if soup.find('title') else ''
    meta = soup.find(
        'meta', {"name": "description"}).attrs['content'] if soup.find(
        'meta', {"name": "description"}) else ''
    return h1, title, meta
