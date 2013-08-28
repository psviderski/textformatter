#!/usr/bin/env python

import argparse
import codecs
import sys

from textformatter import ParagraphReader, TextWidthFormatter


TEXT_ENCODING = 'utf8'


def stdin_width_formatter(max_width):
    reader = codecs.getreader(TEXT_ENCODING)
    stream = reader(sys.stdin)
    paragraph_reader = ParagraphReader(stream)
    width_formatter = TextWidthFormatter(paragraph_reader, max_width=max_width)
    return width_formatter


def main():
    parser = argparse.ArgumentParser(
        description="""Reads text from standard input, then outputs formatted
            to a cpecified width text on standard output."""
    )
    parser.add_argument('-w', '--width', type=int, default=79,
                        help='maximum width (default: 79)')
    args = parser.parse_args()

    width_formatter = stdin_width_formatter(max_width=args.width)
    while True:
        line = width_formatter.readline()
        if not line:
            break
        sys.stdout.write(line.encode(TEXT_ENCODING))


if __name__ == '__main__':
    main()
