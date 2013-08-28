import pytest

from formatters import (AbstractFormatterRule,
                        BreakPunctuationRule,
                        BreakWhitespaceRule,
                        TrailingShortWordRule)


class TestAbstractFormatterRule(object):
    @pytest.fixture
    def rule(self):
        class DummyFormatterRule(AbstractFormatterRule):
            def _check_line_break(self, line_width):
                raise NotImplementedError
        rule = DummyFormatterRule()
        rule.paragraph = u"Sample paragraph."
        return rule

    def test_check_line_break(self, rule):
        assert rule.check_line_break(-10)
        assert rule.check_line_break(0)
        assert rule.check_line_break(len(rule.paragraph))
        assert rule.check_line_break(len(rule.paragraph) + 10)
        with pytest.raises(NotImplementedError):
            rule.check_line_break(1)
        with pytest.raises(NotImplementedError):
            rule.check_line_break(10)
        with pytest.raises(NotImplementedError):
            rule.check_line_break(len(rule.paragraph) - 1)


class TestBreakWhitespaceRule(object):
    @pytest.fixture
    def rule(self):
        rule = BreakWhitespaceRule()
        rule.paragraph = u"Lorem ipsum dolor\n"
        return rule

    def test_check_line_break(self, rule):
        for line_width in (1, 4, 6, 8, 10, 16):
            assert not rule._check_line_break(line_width)
        for line_width in (5, 11, 17):
            assert rule._check_line_break(line_width)


class TestBreakPunctuationRule(object):
    @pytest.fixture
    def rule(self):
        rule = BreakPunctuationRule(max_width=10)
        rule.paragraph =  u".,- aaa -% ? !:; , . abc ? : - , ,bbb"
        rule.allow_break = "1001111111110000000011110000000000111"
        return rule

    def test_check_line_break(self, rule):
        for line_width in xrange(1, len(rule.paragraph)):
            allow_line_break = rule.allow_break[line_width] == "1"
            assert rule._check_line_break(line_width) == allow_line_break


class TestTrailingShortWordRule(object):
    # XXX: It is still unclear how to treat punctuation and compound
    #      words in this rule

    @pytest.fixture
    def rule(self):
        rule = TrailingShortWordRule()
        rule.paragraph =  u"This is a rule to, bla-bla."
        rule.allow_break = "111111000000001100110001000"
        return rule

    @pytest.fixture
    def rule_exception(self):
        rule = TrailingShortWordRule()
        # The whole line only contains short words
        rule.paragraph = u"The for,, a is ,on. at"
        return rule

    def test_check_line_break(self, rule):
        for line_width in xrange(1, len(rule.paragraph)):
            allow_line_break = rule.allow_break[line_width] == "1"
            assert rule._check_line_break(line_width) == allow_line_break

    def test_check_line_break_exception(self, rule_exception):
        for line_width in xrange(1, len(rule_exception.paragraph)):
            assert rule_exception._check_line_break(line_width)
