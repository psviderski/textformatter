"""
Formatters module
"""

import re
import string

from abc import ABCMeta, abstractmethod


NEWLINE_CHAR = u'\n'


class BaseWidthFormatter(object):
    _class_rules = []

    @classmethod
    def ruled(cls, cls_rule, *args, **kwargs):
        cls._class_rules.append((cls_rule, args, kwargs))
        return cls

    def __init__(self, reader, max_width=79, keepends=True):
        self.reader = reader
        self.max_width = max_width
        self.keepends = keepends
        self.paragraph = u""
        # Create instances of the rules
        self.rules = [Rule(*args, max_width=self.max_width, **kwargs)
                      for Rule, args, kwargs in self._class_rules]

    def _check_rules(self, line_width):
        return all(rule.check_line_break(line_width) for rule in self.rules)

    def readline(self):
        if not self.paragraph:
            self.paragraph = self.reader.read()
            if not self.paragraph:
                # The input reader is exhausted
                return self.paragraph
            self.paragraph = self.paragraph.rstrip()
            for rule in self.rules:
                rule.next_paragraph(self.paragraph)
        max_line_width = None
        for line_width in xrange(1, len(self.paragraph) + 1):
            if line_width > self.max_width and max_line_width is not None:
                break
            if not self._check_rules(line_width):
                continue
            # It is possible to break the line on the 'line_width' character
            if line_width <= self.max_width:
                max_line_width = line_width
            else:
                if max_line_width is None:
                    max_line_width = line_width
                break
        if max_line_width is None:
            max_line_width = len(self.paragraph)
        line = self.paragraph[:max_line_width].rstrip()
        self.paragraph = self.paragraph[max_line_width:].lstrip()
        for rule in self.rules:
            rule.break_line(line, self.paragraph)
        if self.keepends:
            line += NEWLINE_CHAR
        return line


class AbstractFormatterRule(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.max_width = kwargs.get('max_width', 79)
        self.paragraph = u""

    def next_paragraph(self, paragraph):
        self.paragraph = paragraph

    def break_line(self, line, paragraph_rest):
        self.paragraph = paragraph_rest

    @abstractmethod
    def _check_line_break(self, line_width):
        pass

    def check_line_break(self, line_width):
        if line_width <= 0 or line_width >= len(self.paragraph):
            return True
        return self._check_line_break(line_width)


class BreakWhitespaceRule(AbstractFormatterRule):
    """Rule to break a line only on a whitespace character.

    Lines cannot be broken in the middle of a word or a run of punctuation
    characters. A word is a run of alphanumeric characters.

    """
    def _check_line_break(self, line_width):
        return self.paragraph[line_width].isspace()


class BreakPunctuationRule(AbstractFormatterRule):
    """Rule to break a line that is a run of punctuation characters.

    A line cannot begin with a punctuation, with the exception of the first
    line in a paragraph, or a run of `max_width` or more characters of
    punctuation and whitespace.

    """
    punctuation_re = re.compile(r'^[{0}\s]+'.format(string.punctuation))

    def _check_line_break(self, line_width):
        next_line = self.paragraph[line_width:].lstrip()
        match = self.punctuation_re.match(next_line)
        if not match:
            return True
        if len(match.group()) >= self.max_width:
            return True
        return False


class TrailingShortWordRule(AbstractFormatterRule):
    """Rule not to end a line with a short word.

    A line cannot end with a word that is `short_word_length` characters
    long or shorter, unless the whole line only contains words that are
    `short_word_length` character long or shorter.

    XXX: It is still unclear how to treat punctuation and compound
         words in this rule.

    """
    def __init__(self, short_word_len=3, **kwargs):
        super(TrailingShortWordRule, self).__init__(**kwargs)
        self.short_word_len = short_word_len
        self.short_word_re = re.compile(r'\b\w{{1,{0}}}$'.format(short_word_len))

    def _check_line_break(self, line_width):
        line = self.paragraph[:line_width].rstrip()
        if not re.search(self.short_word_re, line):
            return True
        # Check if the whole line only contains short words
        for match in re.finditer(r'\w+', line):
            if len(match.group()) > self.short_word_len:
                return False
        return True


def assignrule(cls_rule, *args, **kwargs):
    """Decorator for a formatter class.

    Assigns a given formatter rule class to a decorated formatter class.

    """
    def assignrule_decorator(cls):
        return cls.ruled(cls_rule, *args, **kwargs)
    return assignrule_decorator


@assignrule(TrailingShortWordRule, short_word_len=3)
@assignrule(BreakPunctuationRule)
@assignrule(BreakWhitespaceRule)
class TextWidthFormatter(BaseWidthFormatter):
    """Text width formatter."""
