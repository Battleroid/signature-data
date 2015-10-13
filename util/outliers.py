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

def save_outliers(data, columns, attrs, filename):
    with open(filename, 'w') as f:
        for column in columns:
            avg = attrs[column].avg
            std = attrs[column].std
            labels = ', '.join(data[column])
            f.write('{column} ({total}): '.format(column=column, total=len(data[column])))
            f.write(labels)
            f.write(os.linesep)
        common = set.intersection(*map(set, data.values()))
        if common:
            f.write('Common rows: {}'.format(', '.join(common)))

def flatten(*args):
    for x in args:
        if hasattr(x, '__iter__'):
            for y in flatten(*x):
                yield y
        else:
            yield x

def do_drop(data, outliers, filename='dropped.csv'):
    # Create Ri column by removing 'ARC' from Label and parsing as int
    starting = len(data)
    ri = data['Label'].apply(lambda x: int(x[3:]))
    data.insert(0, 'Ri', ri)
    data.sort_values(['Ri'], inplace=True)
    # Create set from all outliers to avoid dropping already removed labels
    flattened_outliers = list(flatten(outliers.values()))
    outliers_set = set(sorted(flattened_outliers))
    common_outliers = len(flattened_outliers) - len(outliers_set)
    # For each outlier in the set, find its location, drop it in place,
    # then decrement the values for its position and above.
    # Also, WHY THE FUCK DOES REVERSING THE LIST FIX ALL THE ISSUES?
    for o in reversed(list(outliers_set)):
        r = data.loc[data['Label'] == o]
        ridx = r.index
        data.drop(data.index[ridx], inplace=True)
        data.reset_index(inplace=True, drop=True)
        data.ix[data.index >= ridx.item(), 'Ri'] -= 1
        print 'Removed {} (@ {})'.format(o, ridx.item())
    # Reindex and save to file
    data.sort_index(inplace=True)
    data.to_csv(filename)
    print 'From {} rows to {}'.format(starting, len(data))
    print 'Removed a total of {} rows'.format(len(outliers_set))
    print '{} common outliers'.format(common_outliers)

def main(filename, save, drop=False, keep_locuses=False):
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
        save_outliers(outliers, data._get_numeric_data(), column_attrs, save)
    else:
        for column in data._get_numeric_data():
            labels = ', '.join(outliers[column])
            print('{column} ({total}): {labels}'.format(column=column, total=len(outliers[column]), labels=labels))
        common = set.intersection(*map(set, outliers.values()))
        if common:
            print('Common rows: {}'.format(', '.join(common)))
    if drop:
        do_drop(data, outliers, drop)

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args['<file>'], args['-f'], args['--drop'], args['--locuses'])
