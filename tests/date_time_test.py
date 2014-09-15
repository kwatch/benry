# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys, os, re

import unittest
from oktest import ok, test, subject, situation

from benry.date_time import UTCDateTime, LocalDateTime



class UTCDateTime_TC(unittest.TestCase):

    def provide_utc_dt(self):
        return UTCDateTime(2000, 1, 2, 3, 4, 55)


    with subject('#is_utc'):

        @test("[!xed2g] always True.")
        def _(self, utc_dt):
            ok (utc_dt.is_utc).is_(True)


    with subject('#is_local'):

        @test("[!jxzrd] always False.")
        def _(self, utc_dt):
            ok (utc_dt.is_local).is_(False)


    with subject('#offset_minutes'):

        @test("[!z5523] always zero.")
        def _(self, utc_dt):
            ok (utc_dt.offset_minutes) == 0


    with subject('#offset_timedelta'):

        @test("[!jvkda] always zero timedelta.")
        def _(self, utc_dt):
            from datetime import timedelta
            ok (utc_dt.offset_timedelta).is_a(timedelta)
            ok (utc_dt.offset_timedelta.total_seconds()) == 0


    with subject('.now()'):

        @test("[!6etu5] Almost same as datetime.utcnow(), except returning UTCDateTime object.")
        def _(self):
            from datetime import datetime
            utc_now1 = datetime.utcnow()
            utc_dt   = UTCDateTime.now()
            utc_now2 = datetime.utcnow()
            ok (utc_dt).is_a(UTCDateTime)
            ok (utc_dt) >= utc_now1
            ok (utc_dt) <= utc_now2


    with subject('.utcnow()'):

        @test("[!91sgk] (disabled)")
        def _(self):
            def fn(): UTCDateTime.utcnow()
            ok (fn).raises(TypeError, "UTCDateTime: 'utcnow()' is disabled. Use 'now()' instead.")


    with subject('#to_utc()'):

        @test("[!u3vbe] returns self.")
        def _(self, utc_dt):
            ok (utc_dt.to_utc()).is_(utc_dt)


    with subject('#to_local()'):

        @test("[!yrxje] returns local datetime with correct offset.")
        def _(self, utc_dt):
            ok (utc_dt.to_local()).is_a(LocalDateTime)
            ok (str(utc_dt.to_local())) == str(utc_dt + LocalDateTime.offset_timedelta)



class LocalDateTime_TC(unittest.TestCase):

    def provide_local_dt(self):
        return LocalDateTime(2000, 1, 2, 3, 4, 55)


    with subject('#is_utc'):

        @test("[!2up4u] always False.")
        def _(self, local_dt):
            ok (local_dt.is_utc) == False


    with subject('#is_local'):

        @test("[!2f5x9] always True.")
        def _(self, local_dt):
            ok (local_dt.is_local) == True


    with subject('#offset_minutes'):

        @test("[!mpfq5] represents offset from UTC.")
        def _(self, local_dt):
            ok (local_dt.offset_minutes) == 9*60


    with subject('#offset_timedelta'):

        @test("[!9sgvz] represents offset from UTC.")
        def _(self, local_dt):
            from datetime import timedelta
            ok (local_dt.offset_timedelta).is_a(timedelta)
            ok (local_dt.offset_timedelta.total_seconds()) == 9*60*60


    with subject('#now()'):

        @test("[!81zsw] Almost same as datetime.now(), except returning LocalDateTime object.")
        def _(self):
            from datetime import datetime
            dt1 = datetime.now()
            local_dt = LocalDateTime.now()
            dt2 = datetime.now()
            ok (local_dt).is_a(LocalDateTime)
            ok (local_dt) >= dt1
            ok (local_dt) <= dt2


    with subject('.utcnow()'):

        @test("[!why61] (disabled)")
        def _(self):
            def fn(): LocalDateTime.utcnow()
            ok (fn).raises(TypeError, "LocalDateTime: 'utcnow()' is disabled. Use 'now()' instead.")


    with subject('#to_utc()'):

        @test("[!bil7m] returns UTC datetime.")
        def _(self, local_dt):
            ok (local_dt.to_utc()).is_a(UTCDateTime)
            ok (str(local_dt.to_utc())) == str(local_dt - local_dt.offset_timedelta)


    with subject('#to_local()'):

        @test("[!odvwg] returns self.")
        def _(self, local_dt):
            ok (local_dt.to_local()).is_(local_dt)



if __name__ == '__main__':
    import oktest
    oktest.main()
