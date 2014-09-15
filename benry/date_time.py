# -*- coding: utf-8 -*-

###
### $Release: 0.0.0 $
### $Copyright: copyright(c) 2013-2014 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


__all__ = ('UTCDateTime', 'LocalDateTime',)


import sys
from datetime import datetime as _datetime, date as _date, timedelta as _timedelta


class UTCDateTime(_datetime):

    #; [!xed2g] always True.
    is_utc   = True
    #; [!jxzrd] always False.
    is_local = False

    #; [!z5523] always zero.
    offset_minutes   = 0
    #; [!jvkda] always zero timedelta.
    offset_timedelta = _timedelta(seconds=0)

    @classmethod
    def now(cls):
        """[!6etu5] Almost same as datetime.utcnow(), except returning UTCDateTime object."""
        return cls._utcnow()    # _utcnow() is defined later

    def to_utc(self):
        """[!u3vbe] returns self."""
        return self

    def to_local(self):
        """[!yrxje] returns local datetime with correct offset."""
        dt = self + LocalDateTime.offset_timedelta
        return LocalDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)


UTCDateTime._utcnow = UTCDateTime.utcnow
def utcnow(cls):
    """[!91sgk] (disabled)"""
    raise TypeError("UTCDateTime: 'utcnow()' is disabled. Use 'now()' instead.")
UTCDateTime.utcnow = classmethod(utcnow)
del utcnow


class LocalDateTime(_datetime):

    #; [!2up4u] always False.
    is_utc   = False
    #; [!2f5x9] always True.
    is_local = True

    _delta = _datetime.now() - _datetime.utcnow()
    #; [!mpfq5] represents offset from UTC.
    offset_minutes   = round(_delta.total_seconds() / 60.0)
    #; [!9sgvz] represents offset from UTC.
    offset_timedelta = _timedelta(seconds=offset_minutes*60)
    del _delta

    @classmethod
    def now(cls):
        """[!81zsw] Almost same as datetime.now(), except returning LocalDateTime object."""
        pass
    del now

    @classmethod
    def utcnow(cls):
        """[!why61] (disabled)"""
        raise TypeError("LocalDateTime: 'utcnow()' is disabled. Use 'now()' instead.")

    def to_utc(self):
        """[!bil7m] returns UTC datetime."""
        dt = self - self.offset_timedelta
        return UTCDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)

    def to_local(self):
        """[!odvwg] returns self."""
        return self
