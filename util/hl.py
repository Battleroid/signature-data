"""
Usage:
    hl.py [options] <input>

Options:
    -h --help  Show this screen.
    -v --verbose  Verbose messages.
"""

from docopt import docopt
import pandas as pd


def main(args):
    pass


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
