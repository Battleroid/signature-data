# TODO: Add verbose option
"""
Find outliers for each column.

Usage:
    outliers.py [options] <file>
    outliers.py -h | --help

Options:
    -h --help  Show this screen.
    --locuses  Include locuses.
    --drop=<csv>  Drop outliers and save to file.
    -f <output>  Save to file instead of stdout.
"""

import pandas as pd
from docopt import docopt
from collections import namedtuple, defaultdict
import os

attrs = namedtuple('attrs', 'std, avg')

def get_outliers(data, attrs, keep_locuses=False):
    temp = data
    if not keep_locuses:
        locuses = temp.filter(like='Locus').columns
        temp = temp.drop(locuses, axis=1)
    outliers = defaultdict(list)
    for column, val in attrs.items():
        l = 2. * val.std - val.avg
        h = 2. * val.std + val.avg
        for idx in xrange(0, len(temp)):
            x = temp.iloc[idx][column]
            if not(l <= x <= h):
                label = temp.iloc[idx]['Ri']
                outliers[column].append(label)
    return outliers

def save_outliers(data, columns, attrs, filename):
    with open(filename, 'w') as f:
        total = 0
        for column in columns:
            total += len(data[column])
            avg = attrs[column].avg
            std = attrs[column].std
            labels = ', '.join(data[column])
            f.write('{column} (STD: {std}, AVG: {avg}, TOTAL: {total}): '.format(column=column, std=std, avg=avg, total=len(data[column])))
            f.write(labels)
            f.write(os.linesep)
        common = set.intersection(*map(set, data.values()))
        if common:
            f.write('Common rows: {}'.format(', '.join(common)))
        f.write('Total outliers: {}'.format(total))

def flatten(*args):
    for x in args:
        if hasattr(x, '__iter__'):
            for y in flatten(*x):
                yield y
        else:
            yield x

def do_drop_right(data, outliers, filename='dropped.csv'):
    flattened_outliers = list(flatten(outliers.values()))
    outliers_set = set(sorted(flattened_outliers))
    if 'Unnamed: 0' in data.columns:
        data.drop(data[['Unnamed: 0']], axis=1, inplace=True)
    for o in outliers_set:
        r = data.loc[data['Ri'] == o]
        ridx = r.index
        data.drop(data.index[ridx], inplace=True)
        data.reset_index(inplace=True, drop=True)
    data.to_csv(filename, index=False)

def main(filename, save, drop=False, keep_locuses=False):
    data = pd.read_csv(filename)
    column_attrs = dict()
    if not keep_locuses:
        lcs = data.filter(like='Locus').columns
        numeric_columns = data.drop(lcs, axis=1)._get_numeric_data().columns
    else:
        numeric_columns = data._get_numeric_data().columns
    for col in numeric_columns:
        column_attrs[col] = attrs(std=data[col].std(), avg=data[col].mean())
    outliers = get_outliers(data, column_attrs, keep_locuses)
    if save:
        save_outliers(outliers, outliers.keys(), column_attrs, save)
    else:
        for column in data._get_numeric_data():
            labels = ', '.join(outliers[column])
            print('{column} ({total}): {labels}'.format(column=column, total=len(outliers[column]), labels=labels))
        common = set.intersection(*map(set, outliers.values()))
        if common:
            print('Common rows: {}'.format(', '.join(common)))
    if drop:
        do_drop_right(data, outliers, drop)

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args['<file>'], args['-f'], args['--drop'], args['--locuses'])
