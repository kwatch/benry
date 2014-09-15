# -*- coding: utf-8 -*-

import sys, os, re

kookbook.default = 'test'

package   = prop('package', 'benry')
release   = prop('release', '0.0.0')
copyright = prop('copyright', "copyright(c) 2013-2014 kuwata-lab.com all rights reserved")
license   = "MIT License"
basename  = "%s-%s" % (package, release)
python    = prop('python', sys.executable)
vs_home   = prop('vs_home', "/opt/lang")


##
## test task
##

python_versions = (
    '2.5.5',
    '2.6.7',
    '2.7.7',
    '3.0.1',
    '3.1.4',
    '3.2.5',
    '3.3.4',
    '3.4.1',
)

python_binaries = [ (ver, "%s/python/%s/bin/python" % (vs_home, ver))
                      for ver in python_versions ]

@recipe
@spices("-a: run test on Python 2.x and 3.x")
def test(c, *args, **kwargs):
    """do test"""
    if 'a' in kwargs:
        for pyver, pybin in python_binaries:
            print(c%"------- Python $(pyver) -----------")
            system_f(c%"$(pybin) -m oktest tests -sp ")
    else:
        system(c%"python -m oktest tests -sp")


###
### packaging
###

text_files = ['README.rst', 'CHANGES.txt', 'MIT-LICENSE', 'Kookbook.py',
              'MANIFEST.in', #'MANIFEST',
              'setup.py']


class pkg(Category):

    @recipe
    @ingreds('pkg:dist')
    def default(c):
        """create packages"""
        ## setup
        dir = "dist/" + basename
        @pushd(dir)
        def _():
            #system(c%'$(python) setup.py sdist')
            system(c%'$(python) setup.py sdist --force-manifest')
            #system(c%'$(python) setup.py bdist_egg')
        cp(c%'$(dir)/MANIFEST', '.')
        mv(c%'$(dir)/dist/$(package)-$(release).tar.gz', "dist")

    @recipe
    def dist(c, *args, **kwargs):
        """create %s-X.X.X/ directory""" % package
        if release == '0.0.0':
            raise ValueError("release number should be specified")
        ## create dir
        dir = "dist/" + basename
        if os.path.isdir(dir):
            rm_rf(dir)
        mkdir_p(dir)
        ## copy files
        files = [ f for f in text_files if os.path.exists(f) ]
        store(files, dir)
        store(c%'$(package)/**/*.py', 'tests/**/*.py', dir)
        ## edit files
        replacer = [
            (r'\$(Package)\$',   package),
            (r'\$(Release)\$',   release),
            (r'\$(Copyright)\$', copyright),
            (r'\$(License)\$',   license),
            (r'\$(Package):.*?\$',    r'$\1: %s $' % package),
            (r'\$(Release):.*?\$',    r'$\1: %s $' % release),
            (r'\$(Copyright):.*?\$',  r'$\1: %s $' % copyright),
            (r'\$(License):.*?\$',    r'$\1: %s $' % license),
        ]
        edit(c%"$(dir)/**/*", exclude=[c%'$(dir)/Kookbook.py'], by=replacer)
        ##
        replacer2 = [
            (r'\{\{\*(.*?)\*\}\}', r'\1'),
            (r'0\.0\.0', release),
        ]
        edit(c%"$(dir)/README.rst", by=replacer2)
        ## MANIFEST
        #@pushd(dir)
        #def do():
        #    rm_f('MANIFEST')
        #    system(c%'$(python) setup.py sdist --force-manifest')

    @recipe
    def upload(c, *args, **kwargs):
        """upload new version to pypi"""
        dir = "dist/" + basename
        with chdir(dir):
            system(c%"python setup.py register")
            system(c%"python setup.py sdist upload")


kookbook.load('@kook/books/clean.py')
CLEAN.extend(('**/*.pyc', '**/__pycache__', 'lib/*.egg-info', '%s.zip' % package))


@recipe
def task_manifest(c):
    """update MANIFEST file"""
    system(c%'$(python) setup.py sdist --force-manifest')
