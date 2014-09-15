=====
benry
=====

$Release: 0.0.0 $


Useful tools for Python.


benry.rexp
==========


rx()
----

``benry.rexp.rx()`` is a short cut to ``re.compile()``. ::

    from benry.rexp import rx
    
    ## comping -- same as re.compile(r'pat') or re.compile(r'pat', rx.I|rx.S)
    regexp = rx(r'pat')
    regexp = rx(r'pat', rx.I|rx.S)
    
    ## matching -- same as re.compile(r'pat').search(string)
    m = rx(r'pat').search(string)
    
    ## replacing -- same as re.compile(r'pat').sub('repl', string, count=1)
    rx(r'pat').sub('repl', string, count=1)

You don't need to use ``re.xxxx()`` functions because ``rx().xxxx()`` does same things,
and has more features. ::

    ## For example you can't specify starting/ending position with re.match().
    re.match(r'pat', string, re.I)

    ## But you can specify them with rx().match().
    rx(r'pat', re.I).match(string, start_pos, end_pos)


rx.compile()
------------

``rx.compile()`` (or ``benry.rexp.compile()``) is similar to ``re.compile()``,
but the former doesn't cache compiled pattern while the latter caches it.

This is very useful when there are a lot of regexp pattern and they are
no need to cache into library. ::

    mappings = [
        (r'^/posts$',                      'app.PostsPage'),
        (r'^/posts/new$',                  'app.PostCreatePage'),
        (r'^/posts/(?P<id>\d+)$',          'app.PostPage'),
        (r'^/posts/(?P<id>\d+)/edit$',     'app.PostUpdatePage'),
        (r'^/posts/(?P<id>\d+)/comments$', 'app.PostCommentsPage'),
    ]

    ## no need to cache patterns, so calls rx.compile() instead of re.compile()
    from benry.rexp import rx   # or: import compile
    compiled_mappings = [ (rx.compile(pat), cls) for pat, cls in mappings ]


rx.matching()
-------------

``rx.matching()`` (or ``benry.rexp.matching()``) is a utility class to help you
when matching to a lot of patterns.

Without ``rx.matching()``::

    import re

    m = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$', string)
    if m:
        Y, M, D = m.groups()
    else:
        m = re.match(r'^(\d\d)/(\d\d)/(\d\d\d\d)$', string)
        if m:
            M, D, Y = m.groups()
        else:
            m = re.match(r'^(\d\d\d\d)/(\d\d)/(\d\d)$', string)
            if m:
                Y, M, D = m.groups()

With ``rx.matching()``::

    from benry.rexp import rx

    m = rx.matching(string)
    if   m.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$'):
        Y, M, D = m.groups()     # or Y, M, D = m
    elif m.match(r'^(\d\d)/(\d\d)/(\d\d\d\d)$'):
        M, D, Y = m.groups()     # or M, D, Y = m
    elif m.match(r'^(\d\d\d\d)/(\d\d)/(\d\d)$'):
        Y, M, D = m.groups()     # or Y, M, D = m

You can get ``SRE_Match`` object by ``m.matched``. ::

    m = rx.matching(string)
    if m.match(r'pat'):
        print(m.matched.pos)
        print(m.matched.endpos)


type
----

``rx.type`` represents class of regular expression. ::

    import re
    from benry.rexp import rx

    assert rx.type is type(re.compile('x'))



benry.date_time
===============


class UTCDateTime
-----------------

``UTCDdateTime`` is a subclass of ``datetime.datetime`` representing UTC offset. ::

    from benry.date_time import UTCDateTime

    print(UTCDateTime.offset_minutes)      #=> 0
    print(UTCDateTime.offset_timedelta)    #=> timedelta(seconds=0)
    print(UTCDateTime.is_utc)              #=> True
    print(UTCDateTime.is_local)            #=> False

    ## almost same as datetime.utcnow(), except returning UTCDateTime object.
    utc_dt = UTCDateTime.now()

    print(utc_dt.to_utc())                 # returns self.
    print(utc_dt.to_local())               # returns LocalDateTime object.


class LocalDateTime
-------------------

``UTCDdateTime`` is a subclass of ``datetime.datetime`` representing local time.
This class calculates offset between local time and UTC time. ::

    from benry.date_time import LocalDateTime

    print(LocalDateTime.offset_minutes)    #=> 9*60  (ex: JST timezone)
    print(LocalDateTime.offset_timedelta)  #=> timedelta(seconds=9*60*60)
    print(LocalDateTime.is_utc)            #=> False
    print(LocalDateTime.is_local)          #=> True

    ## almost same as datetime.now(), except returning LocalDateTime object.
    local_dt = LocalDateTime.now()

    print(local_dt.to_utc())               # returns UTCDateTime object.
    print(local_dt.to_local())             # returns self.
