# -*- coding: utf-8 -*-
import codecs
import pytest

from StringIO import StringIO
from readers import ParagraphReader


class TestParagraphReader(object):
    read_test_cases = [
        # input text, read length, tuple of successive expected values
        ("aaa\n", None, (u"aaa\n", u"")),
        # newline at the end
        ("aaa bbb ccc", None, (u"aaa bbb ccc\n", u"")),
        # concatenate lines into one
        ("aaa\nbbb\nccc", None, (u"aaa bbb ccc\n", u"")),
        # empty input
        ("", None, (u"", u"")),
        # whitespaces
        ("   \n ", None, (u"\n", u"")),
        ("  \n\n   ", None, (u"\n", u"\n", u"\n", u"")),
        ("\n\n\n", None, (u"\n", u"\n", u"\n", u"")),
        # multiple paragraphs
        ("aaa\n\nbbb\n\n\nccc\n\n", None, (u"aaa\n", u"\n", u"bbb\n", u"\n", u"\n", u"ccc\n", "\n", u"")),
        # CR+LF line endings
        ("aaa\r\nbbb\r\n\r\nccc", None, (u"aaa bbb\n", u"\n", u"ccc\n", u"")),
        # CR line endings
        ("aaa\r\rbbb\r", None, (u"aaa\n", u"\n", u"bbb\n", u"")),
        # mixed line endings
        ("aaa\r\r\nbbb\n\nccc", None, (u"aaa\n", u"\n", u"bbb\n", u"\n", u"ccc\n", u"")),
        # trailing spaces
        ("aaa  \n\n bbb \nccc   ", None, (u"aaa\n", u"\n", u" bbb ccc\n", u"")),
        # unicode
        ("aäa  \n\n ўі ", None, (u"aäa\n", u"\n", u" ўі\n", u"")),
        # custom length
        ("aaa\n", 2, (u"aa", u"a\n", u"")),
        ("aabb\n", 2, (u"aa", u"bb", u"\n", u"")),
        ("aabb\n", 1, (u"a", u"a", u"b", u"b", u"\n", u"")),
        ("a\n\n\n ", 1, (u"a", u"\n", u"\n", u"\n", u"\n", u"")),
        ("a\r\nb\n", 1, (u"a", u" ", u"b", u"\n", u"")),
    ]

    @pytest.fixture(params=read_test_cases)
    def reader_case(self, request):
        input_text, length, expected_values = request.param
        stream = codecs.getreader('utf8')(StringIO(input_text))
        paragraph_reader = ParagraphReader(stream)
        return paragraph_reader, length, expected_values

    @pytest.fixture
    def reader(self):
        stream = codecs.getreader('utf8')(StringIO(""))
        paragraph_reader = ParagraphReader(stream)
        return paragraph_reader

    def test_read(self, reader_case):
        reader, length, expected_values = reader_case
        for expected_value in expected_values:
            #assert reader.read(length) == expected_value
            read = reader.read(length)
            print "Check:", read, expected_value
            assert read  == expected_value

    def test_strip_ending(self, reader):
        assert reader._strip_ending(u"abc\n") == u"abc"
        assert reader._strip_ending(u"abc\r\n") == u"abc"
        assert reader._strip_ending(u"abc\r") == u"abc"
        assert reader._strip_ending(u"abc def  \n") == u"abc def  "
        assert reader._strip_ending(u"\r\n") == u""

    def test_concat_lines(self, reader):
        assert reader._concat_lines(u"", u"") == u""
        assert reader._concat_lines(u"abc", u"") == u"abc"
        assert reader._concat_lines(u"", u"def") == u"def"
        assert reader._concat_lines(u"abc", u"def") == u"abc def"
        assert reader._concat_lines(u"abc ", u"def") == u"abc def"
        assert reader._concat_lines(u"abc", u" def") == u"abc def"
        assert reader._concat_lines(u"abc  ", u" def") == u"abc   def"
        assert reader._concat_lines(u"abc\u2002", u"def") == u"abc\u2002def"
        assert reader._concat_lines(u"abc", u"\u2003def") == u"abc\u2003def"
