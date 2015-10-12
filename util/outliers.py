"""
Find outliers for each column.

Usage:
    outliers.py [--locuses] <file> [-o <output> | --output <output>]
    outliers.py -h | --help

Options:
    -h --help  Show this screen.
    --locuses  Include locuses.
"""

import pandas as pd
from docopt import docopt
from collections import namedtuple, defaultdict


# Attributes for each column
attrs = namedtuple('attrs', 'std, avg')


def main(filename, output, keep_locuses=False):
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
    outliers = defaultdict(list)
    for col, v in column_attrs.items():
        low = 2. * v.std - v.avg
        high = 2. * v.std + v.avg
        for idx in xrange(0, len(data)):
            v = data.iloc[idx][col]
            if not(low <= v <= high):
                outliers[col].append(data.iloc[idx]['Label'])
    # Write results (in order, might as well)
    if not output: output = 'results.txt'
    with open(output, 'w') as f:
        for col in numeric_columns:
            f.write('Column {} ({} total outliers):\n\t{}\n\n'
                    .format(col, len(outliers[col]), ', '.join(outliers[col])))

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args['<file>'], args['<output>'], args['--locuses'])
