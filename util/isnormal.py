"""
Usage:
    isnormal.py [options] <file> <outfile>

Options:
    -v --verbose  Verbose messages.
    -h --help  Show this screen.
"""

import pandas as pd
from docopt import docopt


def quartiles(avg, std):
    vals = []
    for i in range(1, 4):
        vals.append((
            (avg - (i * std)),
            (avg + (i * std))
            ))
    return vals


def main(args):
    # set options and params
    filename = args['<file>']
    outfile = args['<outfile>']
    verbose = args['--verbose']

    # load
    df = pd.read_csv(filename)

    # only select attributes, not locii
    nr = df.filter(like='Nr').columns
    nr = [x for x in nr if 'Locus' not in x]
    attrs = df._get_numeric_data()[nr]

    if verbose:
        print 'Using columnns:', nr
    
    # build quartiles
    nr_quartiles = dict()
    for x in nr:
        avg = attrs[x].mean()
        std = attrs[x].std()
        nr_quartiles[x] = quartiles(avg, std)

    # find records for each and note percentage
    nr_percent = dict()
    for x in nr:
        percentages = []

        # get percentage for each set of ranges (three total)
        for pair in nr_quartiles[x]:
            mask = (attrs[x] >= pair[0]) & (attrs[x] <= pair[1])
            percentages.append(float(len(df.loc[mask])) / len(attrs[x]))
        nr_percent[x] = percentages

    # determine if it is normal
    nr_normal = dict()
    for x in nr:
        n = attrs[x]
        p = nr_percent[x]
        avg = n.mean()
        med = n.median()
        norm = (abs(avg - med) < 4) and (0.65 < p[0] < 0.71) \
                and (0.9 < p[1] < 0.98) and (p[2] > 0.97)
        nr_normal[x] = norm

    # setup results for output
    fields = ['Attribute', 'Normal?', 'avg', 'med', '|avg - med|', '0.65 < x < 0.71', '0.9 < x < 0.98', 'x > 0.97']
    rows = []
    for x in nr:
        avg = attrs[x].mean()
        med = attrs[x].median()
        rows.append([x, nr_normal[x], avg, med, abs(avg - med), nr_percent[x][0], nr_percent[x][1], nr_percent[x][2]])

    # if verbose, print prettytable
    if verbose:
        from prettytable import PrettyTable
        table = PrettyTable()
        table._set_field_names(fields)
        for r in rows:
            table.add_row(r)
        print table

    # save results to csv
    out_df = pd.DataFrame(rows, columns=fields)
    out_df.to_csv(outfile, index=False)


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
