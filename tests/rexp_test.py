# -*- coding: utf-8 -*-

import sys, re
python2 = sys.version_info[0] == 2
python3 = sys.version_info[0] == 3

import unittest
from oktest import ok, test, subject, situation, todo, skip

from benry import rexp

re_pattern_type = type(re.compile('x'))
re_match_type   = type(re.match(r'\w+', 'x'))


class rexp_TC(unittest.TestCase):
    __subject__ = 'benry.rexp'


    with subject('compile()'):

        @test("[!nkd8e] returns compiled regexp object.")
        def _(self):
            ok (rexp.compile('x')).is_a(re_pattern_type)

        @test("[!18aeg] not cache compiled object.")
        def _(self):
            pat = r'^wikxolk$'
            ok ((pat, 0)).not_in(re._cache)
            ok ((pat, 0)).not_in(rexp._cache)
            ok (pat).not_in(rexp._cache)
            rexp.compile(pat)
            ok ((pat, 0)).not_in(re._cache)
            ok ((pat, 0)).not_in(rexp._cache)
            ok (pat).not_in(rexp._cache)


    with subject('rx()'):

        @test("[!jaijg] returns compiled regexp object.")
        def _(self):
            ok (rexp.rx('X')).is_a(re_pattern_type)

        @test("[!w7i3y] caches compiled regexp object.")
        def _(self):
            pat = r'^zxfgui$'
            ok ((pat, 0)).not_in(re._cache)
            ok ((pat, 0)).not_in(rexp._cache)
            ok (pat).not_in(rexp._cache)
            rexp.rx(pat)
            ok ((pat, 0)).not_in(re._cache)
            ok ((pat, 0)).not_in(rexp._cache)
            ok (pat).in_(rexp._cache)

        @test("[!mk6mq] has several shortcuts.")
        def _(self):
            rx = rexp.rx
            ok (rx.compile).is_(rexp.compile)
            ok (rx.type).is_(re_pattern_type)
            ok (rx.Matcher).is_(rexp.Matcher)


    with subject('Matcher'):


        with subject('#__init__()'):

            @test("[!5894d] takes a string.")
            def _(self):
                m = rexp.Matcher("homhom")
                ok (m.string) == "homhom"


        with subject('#match()'):

            @test("[!hisc0] calles re.compile().match() internally.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                ok (m.match(r'\d+')) == None
                ok (m.match(r'\w+')) != None

            @test("[!82wzs] returns matched object if matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                ret = m.match(r'\w+')
                ok (ret).is_a(re_match_type)
                ok (m.matched).is_(ret)

            @test("[!1bghx] returns None if not matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                ret = m.match(r'\d+')
                ok (ret) == None
                ok (m.matched) == None


        with subject('#search()'):

            @test("[!1mlr4] calles re.compile().search() internally.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                ok (m.search(r'\d+')) != None

            @test("[!sn5l4] returns matched object if matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                ret = m.search(r'\d+')
                ok (ret).is_a(re_match_type)
                ok (m.matched).is_(ret)

            @test("[!9bx11] returns None if not matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                ret = m.search(r'[A-Z]+')
                ok (ret) == None
                ok (m.matched) == None


        with subject('#__nonzero__()'):

            @test("[!uvlc2] returns True when matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                m.match(r'\w+')
                ok (m.__nonzero__()) == True
                if python2:
                    ok (bool(m)) == True

            @test("[!qzuo3] returns False when not matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                m.match(r'\d+')
                ok (m.__nonzero__()) == False
                if python3:
                    ok (bool(m)) == False


        with subject('#__bool__()'):

            @test("[!8i8w2] returns True when matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                m.match(r'\w+')
                ok (m.__bool__()) == True
                if python3:
                    ok (bool(m)) == True

            @test("[!9vzm9] returns False when not matched.")
            def _(self):
                m = rexp.Matcher("abc123xyz")
                m.match(r'\d+')
                ok (m.__bool__()) == False
                if python3:
                    ok (bool(m)) == False


        with subject('#__iter__()'):

            @test("[!n6u01] returns iterator of each group.")
            def _(self):
                m = rexp.Matcher("2010-12-31")
                m.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$')
                ok (list(m.__iter__())) == ["2010", "12", "31"]
                Y, M, D = m
                ok (Y) == "2010"
                ok (M) == "12"
                ok (D) == "31"


        with subject('#__getitem__()'):

            @test("[!jjo8m] returns groupdict[key] when key is a string.")
            def _(self):
                m = rexp.Matcher("2010-12-31")
                m.match(r'^(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)$')
                ok (m['year'])  == "2010"
                ok (m['month']) == "12"
                ok (m['day'])   == "31"

            @test("[!ijvmx] returns group(key) when key is an integer.")
            def _(self):
                m = rexp.Matcher("2010-12-31")
                m.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$')
                ok (m[1]) == "2010"
                ok (m[2]) == "12"
                ok (m[3]) == "31"

        @test("#; [!55jnx] has methods and properties same as SRE_Match object.")
        def _(self):
            m = rexp.Matcher("abc123xyz(?P<ext>\.\w+)$")
            m.match(r'.*(\d+)')
            #
            ok (m.end()) == m.matched.end()
            ok (m.end(1)) == m.matched.end(1)
            #
            ok (m.start()) == m.matched.start()
            ok (m.start(1)) == m.matched.start(1)
            #
            ok (m.pos) == m.matched.pos
            ok (m.endpos) == m.matched.endpos
            #
            ok (m.group(1)) == m.matched.group(1)
            ok (m.group(0, 1)) == m.matched.group(0, 1)
            ok (m.groupdict()) == m.matched.groupdict()
            ok (m.groups()) == m.matched.groups()
            #
            ok (m.lastgroup) == m.matched.lastgroup
            ok (m.lastindex) == m.matched.lastindex
            #
            ok (m.re) == m.matched.re
            ok (m.regs) == m.matched.regs
            #
            ok (m.span()) == m.matched.span()
            ok (m.span(1)) == m.matched.span(1)



if __name__ == '__main__':
    import oktest
    oktest.main()
