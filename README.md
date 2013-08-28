# TextFormatter

## Problem

Write a program that takes on its standard input utf8-encoded text of any length, and outputs it on the standard output formatted according to the following rules:

 1. A paragraph is a run of consecutive non-empty lines. Paragraphs are separated by one or more empty lines.
 2. Inside a paragraph, no line can be longer than 79 characters.  The only exception is a line that contains a single word or run of punctuation that is 80 characters, or more, long.
 3. A line cannot begin with a punctuation, with the exception of the first line in a paragraph, or a run of 79 or more characters of punctuation and whitespace.
 4. A line cannot end with a word that is 3 characters long or shorter, unless the whole line only contains words that are 3 character long or shorter.
 5. Lines cannot be broken in the middle of a word. A word is a run of alphanumeric characters.
 6. Lines cannot be broken in the middle of a run of punctuation characters.
 7. No additional whitespace can be inserted, except for a newline at the end of a line, or a space before a word. If there is no space between a word and a punctuation, no space can be added there. There should be no whitespace at the end of the line, except for the newline character.
 8. All the lines in a paragraph, except for the last one, have to be as long as possible.
 9. If the whole text doesn't end with a newline character, an additional newline character is generated at the end.

## Usage

    ./format.py < text_file

## Help

    python $ ./format.py --help
    usage: format.py [-h] [-w WIDTH]

    Reads text from standard input, then outputs formatted to a cpecified width
    text on standard output.

    optional arguments:
      -h, --help            show this help message and exit
      -w WIDTH, --width WIDTH
                            maximum width (default: 79)
