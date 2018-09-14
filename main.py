# coding: utf8
import re
import time

import requests

CROWLER_DELAY = 3
PROTOCOL_PATTERN = re.compile(r'^(?P<protocol>[a-z]+)://')
DOMEN_PATTERN = re.compile(r'http[s]{0,1}://(?P<domen>[A-Za-z0-9._-]+)')
LINK_PATTERN = re.compile(r'href="(?P<link>[A-Za-z0-9?&=/:.]+)"')


def work_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        ret_value = func(*args, **kwargs)
        print('{}: {}s'.format(func.__name__, time.time() - start))
        return ret_value
    return wrapper


def full_url(protocol, domen, uri=''):
    sep = '' if uri.startswith('/') or uri == '' else '/'
    return '{}://{}{}{}'.format(protocol, domen, sep, uri)


def get_html_by_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print('ERROR\t{}: (Status code {} != 200)'.format(
                url, response.status_code
            ))
            return ''
        print('OK\t{}'.format(url))
        return response.text
    except Exception as e:
        print('ERROR\t{}: ({} {})'.format(url, type(e), e)) 
        return ''


def get_links_from_html(html):
    return LINK_PATTERN.findall(html)

 
def get_text_from_html(html):
    return ''


def get_bag_of_words(text):
   return []


def simplify_bag_of_words(bag_of_words):
    return []


def get_url_index(bag_of_words):
    return {}


def filter_invalid_links(links, domen):
    domen_pattern = re.compile(r'http[s]{0,1}://' + domen + '')

    filtered = set()
    for link in links:
        if not link.startswith('http') and '//{}/'.format(domen) not in link:
            filtered.add(link)
    return filtered


def filter_visited_links(links, visited):
    return list(set(links).difference(visited))


def normalize_links(links, protocol_domen, url):
    protocol = PROTOCOL_PATTERN.search(url).groupdict()['protocol']
    domen = DOMEN_PATTERN.search(url).groupdict()['domen']

    normalized = []
    for link in links:
        if link.startswith('http'):
            normalized.append(link)
        else:
            url = url if url.endswith('/') else '{}/'.format(url)
            prefix = full_url(protocol, domen) if link.startswith('/') else url
            normalized.append('{}{}'.format(prefix, link))
    return normalized


def crowler(url, visited=None, depth=5):
    visited = set(visited) if visited else set()
    visited.add(url)

    protocol = PROTOCOL_PATTERN.search(url).groupdict()['protocol']
    domen = DOMEN_PATTERN.search(url).groupdict()['domen']
    html = get_html_by_url(url)

    text = get_text_from_html(html)
    bag_of_words = get_bag_of_words(text)
    bag_of_words = simplify_bag_of_words(bag_of_words)
    url_index = {url: get_url_index(bag_of_words)}

    links = get_links_from_html(html)
    links = filter_invalid_links(links, domen)
    links = normalize_links(links, full_url(protocol, domen), url)
    links = filter_visited_links(links, visited) 

    if depth - 1 <= 0:
        print('maximum depth achieved.')
        return {}, visited

    for link in links:
        print('    {}'.format(link))
    print('url: {}, depth: {}, links: {}, visited: {}'.format(url, depth, len(links), len(visited))) 

    for link in links:
        time.sleep(CROWLER_DELAY)
        sub_url_index, visited = crowler(link, visited, depth - 1)
        url_index[link] = sub_url_index
                
    return url_index, visited
    

@work_time
def main():
    visited = crowler('http://stankin.ru/', depth=3)
    print(visited)


if __name__ == '__main__':
    main()

