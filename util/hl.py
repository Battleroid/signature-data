"""
Usage:
    hl.py [options] <input> <output>

Options:
    -h --help  Show this screen.
    -v --verbose  Verbose messages.
"""

from docopt import docopt
import pandas as pd


def pair(l):
    "pair single list by getting opposite steps (even/odd) pairs"
    return zip(l[::2], l[1::2])


def main(args):
    # load
    df = pd.read_csv(args['<input>'])
    results_df = pd.DataFrame({'Calculated HL': []})

    # setup locii
    nr_cols = df.filter(like='Nr').columns
    locii_cols = pair(nr_cols)
    pair_h = dict()

    # calculate per locus (pair) H (H ith)
    for p in locii_cols:
        p1, p2 = p[0], p[1]
        combined = pd.concat([df[p1], df[p2]])
        freqs = [pow(float(x) / len(combined), 2)
                for x in combined.value_counts()]
        pair_h[p1] = 1 - sum(freqs)

    # calculate HL for each record
    for idx in range(len(df)):
        row = df.iloc[idx]
        he, ho = 0.0, 0.0
        for l, n in locii_cols:
            a, b = row[l], row[n]
            if a == b:
                ho += pair_h[l]
            else:
                he += pair_h[l]
        r = float(ho) / (float(ho) + float(he))
        results_df = results_df.append(pd.DataFrame({'Calculated HL': [r]}))

    # correct index on results (not necessary, but nicer to read)
    results_df.index = range(1, len(results_df) + 1)
    results_df.index = 'R' + results_df.index.astype(str)
    results_df.index.name = 'Ri'

    # save
    results_df.to_csv(args['<output>'])


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
