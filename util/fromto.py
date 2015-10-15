"""
Usage:
    fromto.py [options] (tocsv | toexcel) <source> <output>

Options:
    -h --help  Show this screen.
    --index  Include an automatic index.
"""

from docopt import docopt
import pandas

def to_csv(source, output, index=False):
    df = pandas.read_excel(source)
    df.to_csv(output, index=index)

def to_excel(source, output, index=False):
    df = pandas.read_csv(source)
    df.to_excel(output, index=index)

def main(args):
    index = args['--index']
    source = args['<source>']
    output = args['<output>']
    if args['tocsv']:
        to_csv(source, output, index)
    if args['toexcel']:
        to_excel(source, output, index)

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
