"""
Usage:
    corr.py [options] <file> <outfile>

Options:
    -v --verbose  Verbose messages.
    -h --help  Show this screen.
"""


import pandas as pd
from docopt import docopt


def main(args):
    # setup options and params
    filename = args['<file>']
    outfile = args['<outfile>']
    verbose = args['--verbose']

    # load
    df = pd.read_csv(filename)

    # exclude locii
    nr = df.filter(like='Nr').columns
    nr = [x for x in nr if 'Locus' not in x]
    attrs = df._get_numeric_data()[nr]

    # show cols
    if verbose:
        print 'Using columns:', nr

    # build list of correlations
    corr_df = pd.DataFrame(columns=nr, index=nr)
    for x in attrs:
        x_df = attrs[x]
        for y in attrs:
            y_df = attrs[y]
            corr_df[x][y] = x_df.corr(y_df)

    # save 
    corr_df.to_csv(outfile)

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
