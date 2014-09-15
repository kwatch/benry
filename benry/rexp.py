# -*- coding: utf-8 -*-

###
### $Release: 0.0.0 $
### $Copyright: copyright(c) 2013-2014 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


__all__ = ('rx', 'compile', 'matching',)


import sys

from sre_compile import compile as _compile    # ok: CPython, PyPy


def compile(pattern, flags=0):
    """Similar to re.compile(), but no caching."""
    #; [!nkd8e] returns compiled regexp object.
    #; [!18aeg] not cache compiled object.
    return _compile(pattern, flags)


_cache = {}         # TODO: weakref?
#_MAXCACHE = 2048

def rx(pattern, flags=0):
    """Almost same as re.compile()."""
    #; [!jaijg] returns compiled regexp object.
    #; [!w7i3y] caches compiled regexp object.
    key = (pattern, flags) if flags else pattern
    try:
        return _cache[key]
    except KeyError:
        _cache[key] = compiled = compile(pattern, flags)
    return compiled


class matching(object):
    """
    ex:
       from rexp import rx
       m = rx.matching("12/31/2014")
       if m.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$'):
           Y, M, D = m.groups()   # or: Y, M, D = m
       elif m.match(r'^(\d\d)/(\d\d)/(\d\d\d\d)$'):
           M, D, Y = m.groups()   # or: M, D, Y = m
       elif m.match(r'^(\d\d\d\d)/(\d\d)/(\d\d)$'):
           Y, M, D = m.groups()   # or: M, D, Y = m
       else:
           Y = M = D = None
       print("year: %s, month: %s, day: %s" % (Y, M, D))
    """

    def __init__(self, string):
        #; [!5894d] takes a string.
        self.string = string
        self.matched = None

    def match(self, pattern, flags=0):
        #; [!hisc0] calles re.compile().match() internally.
        #; [!82wzs] returns matched object if matched.
        #; [!1bghx] returns None if not matched.
        self.matched = matched = rx(pattern, flags).match(self.string)
        return matched

    def search(self, pattern, flags=0):
        #; [!1mlr4] calles re.compile().search() internally.
        #; [!sn5l4] returns matched object if matched.
        #; [!9bx11] returns None if not matched.
        self.matched = matched = rx(pattern, flags).search(self.string)
        return matched

    def __nonzero__(self):
        #; [!uvlc2] returns True when matched.
        #; [!qzuo3] returns False when not matched.
        return self.matched is not None

    def __bool__(self):
        #; [!8i8w2] returns True when matched.
        #; [!9vzm9] returns False when not matched.
        return self.matched is not None

    def __iter__(self):
        #; [!n6u01] returns iterator of each group.
        return self.matched.groups().__iter__()

    def __getitem__(self, key):
        #; [!jjo8m] returns groupdict()[key] when key is a string.
        if isinstance(key, str):
            return self.matched.groupdict()[key]
        #; [!ijvmx] returns group(key) when key is an integer.
        else:
            return self.matched.group(key)

    #; [!55jnx] has methods and properties same as SRE_Match object.

    def end(self, group=0):
        return self.matched.end(group)

    @property
    def endpos(self):
        return self.matched.endpos

    def expand(self, template):
        return self.matched.expand(template)

    def group(self, *args):
        return self.matched.group(*args)

    def groupdict(self, default=None):
        return self.matched.groupdict(default)

    def groups(self, default=None):
        return self.matched.groups(default)

    @property
    def lastgroup(self):
        return self.matched.lastgroup

    @property
    def lastindex(self):
        return self.matched.lastindex

    @property
    def pos(self):
        return self.matched.pos

    @property
    def re(self):
        return self.matched.re

    @property
    def regs(self):
        return self.matched.regs

    def span(self, group=None):
        if group is None:
            return self.matched.span()
        else:
            return self.matched.span(group)

    def start(self, group=0):
        return self.matched.start(group)

    #@property
    #def string(self):
    #    return self.matched.string


#; [!mk6mq] has several shortcuts.
rx.compile = compile
rx.type    = type(_compile('x'))
rx.matching = matching


#; [!ijpox] has same options with re module.
import re
rx.I = re.I
rx.L = re.L
rx.M = re.M
rx.S = re.S
rx.U = re.U
rx.X = re.X
rx.IGNORECASE = re.IGNORECASE
rx.LOCALE     = re.LOCALE
rx.MULTILINE  = re.MULTILINE
rx.DOTALL     = re.DOTALL
rx.UNICODE    = re.UNICODE
rx.VERBOSE    = re.VERBOSE
del re
