import datetime
import time
from os.path import join

import pandas as pd
from DLBio.helpers import MyDataFrame
from mdutils.mdutils import MdUtils
from read_em_results import create_match_table

PATH = 'em_results.csv'
PLAYER_RESULTS = 'player_results'


def run(write_file=True, read_from_file=True):
    players = {
        'Manja': evaluate('manja.md', read_from_file),
        'Philipp (Bot)': evaluate('philipp.md', read_from_file),
        'Felix': evaluate('felix.md', read_from_file),
        'Hans-Peter (Bot)': evaluate('hans_peter.md', read_from_file),
        'Laura': evaluate('laura.md', read_from_file),
    }

    df = MyDataFrame()
    for name, val in players.items():
        df.update({
            'name': name,
            'accuracy': (1. - (val['points'] == 0).mean()).round(2),
            'points': val['points'].sum(),
        })

    df = df.get_df().sort_values('points', ascending=False)
    print(df)

    if write_file:
        path = 'README.md'
    else:
        path = 'tmp.md'

    md_file = MdUtils(file_name=path, title='em_football')
    md_file.new_header(level=1, title='Leaderboard')
    md_file.new_paragraph(df.to_markdown())

    md_file.new_header(level=2, title='Rules')
    md_file.new_paragraph(
        "Predicting the right result: 3 Points. Predicting the right winner or draw: 1 Point. Accuracy: number of correct winner/draw predictions divided by total number of games."
    )

    md_file.new_header(level=1, title="Each player's prediction:")
    for player, tmp in players.items():
        md_file.new_header(level=2, title=player)
        md_file.new_paragraph(tmp.to_markdown())

    md_file.create_md_file()


def evaluate(path, read_from_file):
    if read_from_file:
        gt = pd.read_csv(PATH)
    else:
        # crawl data from the net
        gt = create_match_table()

    gt['ts'] = [to_time(row) for _, row in gt.iterrows()]
    gt = gt.sort_values('ts', ascending=True)
    df = read_markdown(join(PLAYER_RESULTS, path))

    output = MyDataFrame()

    for i in range(gt.shape[0]):
        y = gt.iloc[i]
        x = df[df['team1'] == y['team1']]
        x = x[x['team2'] == y['team2']]
        x = x.iloc[0, :]

        tmp = x['result'].split('-')
        g1 = int(tmp[0])
        g2 = int(tmp[1])

        perfect_match = g1 == y['g1'] and g2 == y['g2']
        if perfect_match:
            points = 3
        elif (g1 > g2) and (y['g1'] > y['g2']):
            # right class
            points = 1
        elif (g2 > g1) and (y['g2'] > y['g1']):
            # right class
            points = 1
        elif (g2 == g1) and (y['g2'] == y['g1']):
            points = 1
        else:
            points = 0

        output.update({
            'team1': y['team1'],
            'team2': y['team2'],
            'prediction': x['result'],
            'result': f'{y["g1"]}-{y["g2"]}',
            'points': points
        })

    output = output.get_df()
    return output


def read_markdown(path):
    do_save = False
    md_table = []

    with open(path, 'r') as file:
        for line in file.readlines():
            if line:
                line = line.replace('\n', '')

            if line == "## All Matches":
                do_save = True
                continue

            if do_save and line != '':
                md_table.append(line)

    df = MyDataFrame()
    header = md_table[0].split('|')[1:-1]
    header = [key.strip() for key in header]
    for line in md_table[2:]:
        line = line.split('|')[1:-1]
        tmp = dict()
        for idx, key in enumerate(header):
            tmp[key] = line[idx].strip()

        df.update(tmp)

    df = df.get_df().iloc[:, 1:]
    return df


def to_time(row):
    dtime = datetime.datetime(
        year=2000 + int(row['year']), month=int(row['month']),
        day=int(row['day']), hour=int(row['hour']), minute=int(row['minute'])
    )
    timestamp = dtime.timestamp()
    return timestamp


if __name__ == '__main__':
    run()
