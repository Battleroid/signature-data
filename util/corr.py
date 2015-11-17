"""
Usage:
    corr.py [options] <file> <outfile>

Options:
    -v --verbose  Verbose messages.
    -c --coef  Use own correlation coefficient process, not from Pandas.
    -h --help  Show this screen.
"""


import pandas as pd
from docopt import docopt


def corr_coef(df, a, b):
    a_std, b_std = df[a].std(), df[b].std()
    a_avg, b_avg = df[a].mean(), df[b].mean()
    pairs = zip(df[a], df[b])
    r = sum([(ai - a_avg) * (bi - b_avg) for ai, bi in pairs]) / (float(len(df[a])) * a_std * b_std)
    return r


def main(args):
    # setup options and params
    filename = args['<file>']
    outfile = args['<outfile>']
    use_own = args['--coef']
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
        print 'Using {} correlation coefficient.'.format('own' if use_own else 'Pandas')

    # build list of correlations
    if use_own:
        corr_df = pd.DataFrame(columns=nr, index=nr)
        for x in attrs:
            x_df = attrs[x]
            for y in attrs:
                y_df = attrs[y]
                corr_df[x][y] = corr_coef(attrs, x, y)
    else:
        corr_df = attrs.corr()

    # save 
    corr_df.to_csv(outfile)

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
