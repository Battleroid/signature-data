"""
Find outliers for each column.

Usage:
    outliers.py [--locuses] <file> [-f <output>]
    outliers.py -h | --help

Options:
    -h --help  Show this screen.
    --locuses  Include locuses.
    -f <output>  Save to file instead of stdout.
"""

import pandas as pd
from docopt import docopt
from collections import namedtuple, defaultdict
import os

attrs = namedtuple('attrs', 'std, avg')

def get_outliers(data, attrs):
    outliers = defaultdict(list)
    for column, val in attrs.items():
        l = 2. * val.std - val.avg
        h = 2. * val.std + val.avg
        for idx in xrange(0, len(data)):
            x = data.iloc[idx][column]
            if not(l <= x <= h):
                label = data.iloc[idx]['Label']
                outliers[column].append(label)
    return outliers

def save_results(data, columns, filename):
    with open(filename, 'w') as f:
        for column in columns:
            labels = ', '.join(data[column])
            f.write('{column} ({total}): '.format(column=column, total=len(data[column])))
            f.write(labels)
            f.write(os.linesep)
        common = set.intersection(*map(set, data.values()))
        if common:
            f.write('Common rows: {}'.format(', '.join(common)))

def main(filename, save, keep_locuses=False):
    data = pd.read_csv(filename)
    locuses = data.filter(like='Locus').columns
    # Drop locuses if not needed
    if not keep_locuses:
        data.drop(locuses, axis=1, inplace=True)
    # Collect attributes for each column with numeric data
    column_attrs = dict()
    numeric_columns = data._get_numeric_data().columns
    for col in numeric_columns:
        column_attrs[col] = attrs(std=data[col].std(), avg=data[col].mean())
    # Collect outliers
    outliers = get_outliers(data, column_attrs)
    # Save or echo results
    if save:
        save_results(outliers, data._get_numeric_data(), save)
    else:
        for column in data._get_numeric_data():
            labels = textwrap.dedent(', '.join(outliers[column])).strip()
            print('{column} ({total}): {labels}'.format(column=column, total=len(outliers[column]), labels=labels))
        common = set.intersection(*map(set, outliers.values()))
        if common:
            print('Common rows: {}'.format(', '.join(common)))

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args['<file>'], args['-f'], args['--locuses'])
