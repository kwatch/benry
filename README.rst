=====
benry
=====

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
