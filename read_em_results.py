import re
from os.path import isfile

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.exceptions import Timeout

from helpers import MyDataFrame

URL = 'https://www.fussball-wm.pro/em-2021/tabellen-ergebnisse/'

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


def create_match_table():
    try:
        req = requests.get(URL, HEADERS, timeout=(10, 10))
    except Timeout:
        if isfile('em_results.csv'):
            return
        else:
            req = requests.get(URL, HEADERS, timeout=(30, 30))

    soup = BeautifulSoup(req.content, 'html.parser')
    tables_ = soup.findAll('table')

    df = MyDataFrame()
    for table in tables_:
        for row in table.findAll('tr'):
            x = row.findAll('td')
            if not x:
                continue

            tmp = get_date(x[0].text, x[1].text)

            teams_ = x[2].text.replace('Nordmazedonien', 'Mazedonien')
            team1, team2 = teams_.split(' – ')
            g1, g2 = x[3].text.split(':')

            # game not played yet
            if g1 == '-':
                continue

            tmp.update({
                'team1': team1,
                'team2': team2,
                'g1': int(g1),
                'g2': int(g2),
            })

            df.update(tmp)

    df = df.get_df()
    df.to_csv('em_results.csv')
    return df


def get_date(x, y):
    rgx = r'(.*)(\d\d).(\d\d).(\d\d)'
    match = re.match(rgx, x)

    hour, minute = y.split(':')

    return {
        'day': match.group(2),
        'month': match.group(3),
        'year': match.group(4),
        'hour': hour,
        'minute': minute
    }


if __name__ == '__main__':
    create_match_table()
