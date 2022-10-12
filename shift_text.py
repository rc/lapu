#!/usr/bin/env python
"""
Shift a text coming to stdin and print it to stdout.
"""
from argparse import RawDescriptionHelpFormatter, ArgumentParser
import sys

def main():
    parser = ArgumentParser(description=__doc__.rstrip(),
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--shift', metavar='int', type=int,
                        action='store', dest='shift',
                        default=4)
    options = parser.parse_args()

    shift = ' ' * options.shift
    for line in sys.stdin:
        sys.stdout.write(shift + line)

if __name__ == '__main__':
    main()
