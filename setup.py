###
### $Release: 0.0.0 $
### $Copyright: copyright(c) 2013-2014 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, re, os
#arg1 = len(sys.argv) > 1 and sys.argv[1] or None
#if arg1 == 'egg_info':
#    from ez_setup import use_setuptools
#    use_setuptools()
#if arg1 == 'bdist_egg':
#    from setuptools import setup
#else:
#    from distutils.core import setup
arg1 = len(sys.argv) > 1 and sys.argv[1] or None
if arg1 == 'sdist':
    from distutils.core import setup
else:
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup


def fn():
    name             = '$Package$'
    version          = '$Release$'
    author           = 'makoto kuwata'
    author_email     = 'kwa@kuwata-lab.com'
    #maintainer       = author
    #maintainer_email = author_email
    #url              = 'http://packages.python.org/benry/'
    url              = 'https://pypi.python.org/pypi/benry'
    description      = 'Experimental utilities for Python'
    long_description = open("README.rst").read()
    download_url = 'https://pypi.python.org/packages/source/b/$Package$/$Package$-$Release$.tar.gz'
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        #'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.0',
        #'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
    platforms    = 'any'
    license      = '$License$'

    #py_modules   = ['benry']
    #package_dir  = {'': 'lib'}
    #scripts     = ['bin/benry.py']
    packages    = ['benry']
    #zip_safe     = False

    return locals()


setup(**fn())
