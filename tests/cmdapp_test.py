# -*- coding: utf-8 -*-

import sys, os, re
from datetime import datetime, date
import unittest

from oktest import ok, test, NG, skip, todo, at_end, subject, situation
from oktest.dummy import dummy_io


from benry.cmdapp import (
    Application, App, Action, CommandOptionError,
    Option, OptionParser, OptionDefinitionError,
    find_by, find_index, _B,
)



class Action_TC(unittest.TestCase):


    with subject(".new()"):

        @test("[!rf00z] returns new Action object.")
        def _(self):
            fn = lambda: None
            obj = Action.new("cp src dst", "copy file", fn, [], alias=None)
            ok (obj).is_a(Action)
            ok (obj.desc) == "copy file"
            ok (obj.func) == fn
            ok (obj.options) == []
            ok (obj.alias) == None

        @test("[!3g317] parses action definition string.")
        def _(self):
            obj = Action.new("cp src dst", "copy file", None, [], alias="dup")
            ok (obj.name) == "cp"
            ok (obj.argdef) == "src dst"
            ok (obj.alias) == "dup"


    with subject(".#parse()"):

        @test("[!e9psb] strips action definition string.")
        def _(self):
            ret = Action.parse("  cp src dst  ")
            ok (ret) == ("cp", "src dst")

        @test("[!pe0b5] parses string, and returns action name and argument definition.")
        def _(self):
            ret = Action.parse("cp src dst")
            ok (ret) == ("cp", "src dst")


    with subject(".__call__()"):

        @test("[!tm64g] invokes func with arguments.")
        def _(self):
            def func(arg):
                called[0] = arg
                return "ok"
            called = [None]
            action = Action.new("test", "test", func, [])
            ok (called[0]) == None
            ok (action(123)) == "ok"
            ok (called[0]) == 123


    with subject("#format_options()"):

        @test("[!s2ip2] returns command-option help string.")
        def _(self):
            opts = [
                Option.new("-h, --help",       "show help"),
                Option.new("-f, --file=FILE",  "filename"),
                Option.new("-i, --indent[=width]", "indent width (default 2)"),
                Option.new("--version",        "show version"),
                Option.new("-D level",         "debug mode"),
                Option.new("-d",               "same as -D2"),
            ]
            fn = lambda *args, **kwargs: None
            action = Action.new("hist", "show history", fn, opts)
            ok (action.format_options(width=15, indent=2)) == r"""
  -h, --help     : show help
  -f, --file=FILE: filename
  -i, --indent[=width]: indent width (default 2)
      --version  : show version
  -D level       : debug mode
  -d             : same as -D2
"""[1:]



class Option_TC(unittest.TestCase):


    with subject(".new()"):

        @test("[!k25na] returns new Option object.")
        def _(self):
            ret = Option.new("-h, --help", "show help")
            ok (ret).is_a(Option)

        @test("[!8s9ue] parses option definition string.")
        def _(self):
            fn_validate = lambda val: val.isdigit() or "integer requried."
            fn_convert  = lambda val: 2 if val is True else int(val)
            fn_operate  = lambda val, opts: opts.__setitem__('indent', val)
            ret = Option.new("-i, --indent[=d]", "indent (default 2)",
                             validate=fn_validate, convert=fn_convert, operate=fn_operate)
            ok (ret).attr("short", "i").attr("long", "indent").attr("desc", "indent (default 2)")
            ok (ret.arg_name) == "d"
            ok (ret.arg_required) == False
            ok (ret.arg_type) == None
            ok (ret.validate) == fn_validate
            ok (ret.convert)  == fn_convert
            ok (ret.operate)  == fn_operate


    with subject(".#parse()"):

        @test("[!yxg3b] parses both short and long option defstr.")
        def _(self):
            parse = Option.parse
            ok (parse("-h,  --help"))       == ("h", "help",   None,   None)
            ok (parse("-f,   --file=FILE")) == ("f", "file",   "FILE", True)
            ok (parse("-i,\t--indent[=N]")) == ("i", "indent", "N",    False)

        @test("[!z51ip] parses short options defstr.")
        def _(self):
            parse = Option.parse
            ok (parse("-h"))       == ("h", None, None,   None)
            ok (parse("-f\tFILE")) == ("f", None, "FILE", True)
            ok (parse("-i[N]"))    == ("i", None, "N",    False)

        @test("[!70euy] parses long option defstr.")
        def _(self):
            parse = Option.parse
            ok (parse("--help"))       == (None, "help",   None,   None)
            ok (parse("--file=FILE"))  == (None, "file",   "FILE", True)
            ok (parse("--indent[=N]")) == (None, "indent", "N",    False)

        @test("[!5nqu9] raises OptionDefinitionError when invalid option definition string.")
        def _(self):
            parse = Option.parse
            def fn(): parse("-h,--help")
            ok (fn).raises(OptionDefinitionError, "-h,--help: invalid option definition.")

        @test("[!0ifmd] strips option definition string.")
        def _(self):
            parse = Option.parse
            ok (parse("  -h,  --help\n"))         == ("h", "help",   None,   None)
            ok (parse("\t-f,   --file=FILE  "))   == ("f", "file",   "FILE", True)
            ok (parse("\n-i,\t--indent[=N]\t\t")) == ("i", "indent", "N",    False)


    with subject("#format()"):

        def provide_newopt(self):
            def newopt(short, long, arg_name, arg_required):
                return Option(short, long,  None, arg_name=arg_name, arg_required=arg_required)
            return newopt

        @test("[!dljh9] returns string such as '-h, --help' when option takes no arg.")
        def _(self, newopt):
            ok (newopt("f",  "file", None, None).format()) == "-f, --file"
            ok (newopt(None, "file", None, None).format()) == "    --file"
            ok (newopt("f",  None,   None, None).format()) == "-f"

        @test("[!je9ya] returns string such as '-f, --file=FILE' when option takes required arg.")
        def _(self, newopt):
            ok (newopt("f",  "file", "FILE", True).format()) == "-f, --file=FILE"
            ok (newopt(None, "file", "FILE", True).format()) == "    --file=FILE"
            ok (newopt("f",  None,   "FILE", True).format()) == "-f FILE"

        @test("[!s49hx] returns string such as '-i, --indent[=N]' when optoin takes optional arg.")
        def _(self, newopt):
            ok (newopt("f",  "file", "FILE", False).format()) == "-f, --file[=FILE]"
            ok (newopt(None, "file", "FILE", False).format()) == "    --file[=FILE]"
            ok (newopt("f",  None,   "FILE", False).format()) == "-f[FILE]"



class OptionParser_TC(unittest.TestCase):

    def provide_parser(self):
        optdefs = [
            Option.new("-h, --help",          "show help"),
            Option.new("-v, --version",       "print version"),
            Option.new("-f, --file=FILE",     "filename"),
            Option.new("-i, --indent[=num]",  "indent (default 2)",
                       validate=lambda val: val is True or val.isdigit() or "integer expected."),
            Option.new("-D, --debug[=level]", "debug level (default 1)",
                       validate=[
                           lambda val: val is True or val.isdigit() or "integer expected.",
                           lambda val: 1 <= int(val) <= 3  or "out of range (expected 1..3).",
                       ]),
            Option.new("-d, --date=DATE",     "date (YYYY-MM-DD)",
                       validate=lambda val: re.match(r'^\d\d\d\d-\d\d-\d\d$', val) or "YYYY-MM-DD expected",
                       convert=lambda val: datetime.strptime(val, '%Y-%m-%d').date()),
            Option.new("-I, --include=PATH",   "include path",
                       operate=(lambda optval, optdict:
                                  optdict.setdefault('include', []).append(optval))),

        ]
        return OptionParser(optdefs)


    with subject("#parse()"):

        @test("[!5eerp] '-' should be regard as argument, not option string.")
        def _(self, parser):
            args = ["-", "-h"]
            optdict = parser.parse(args)
            ok (args) == ["-", "-h"]
            ok (optdict) == {}

        @test("[!vmcdf] parses long options of action.")
        def _(self, parser):
            args = [
                "--help",             # no arg
                "--file=file.txt",    # required arg
                "--indent=4",         # optional arg
                "--debug",            # optional arg
                "arg1",
                "arg2",
            ]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "file": "file.txt", "indent": "4", "debug": True}

        @test("[!b6178] parses short options of action.")
        def _(self, parser):
            args = [
                "-h",                # no arg
                "-f", "file.txt",    # required arg
                "-i4",               # optional arg
                "-D",                # optional arg
                "arg1",
                "arg2",
            ]
            #
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "file": "file.txt", "indent": "4", "debug": True}
            #
            args = ["-hffile.txt", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "file": "file.txt"}

        @test("[!ugy1h] stops to parse action options when arg is '--'.")
        def _(self, parser):
            args = [
                "-hffile.txt",     # parsed
                "--",              # skip parsing
                "-i",
                "--debug",
                "arg1",
                "arg2",
            ]
            optdict = parser.parse(args)
            ok (args) == ["-i", "--debug", "arg1", "arg2"]
            ok (optdict) == {"help": True, "file": "file.txt"}

        @test("[!ktzbb] raises error when long option requires arg but not specified.")
        def _(self, parser):
            args = ["--file", "arg1", "arg2"]
            def fn(): parser.parse(args)
            ok (fn).raises(CommandOptionError, "--file: argument required.")

        @test("[!mzzd4] raises error when long option doesn't require arg but specified.")
        def _(self, parser):
            args = ["--help=message", "arg1", "arg2"]
            def fn(): parser.parse(args)
            ok (fn).raises(CommandOptionError, "--help=message: unexpected argument.")

        @test("[!tzuoh] raises error when invalid format long option.")
        def _(self, parser):
            args = ["--file:hom.txt"]
            def fn(): parser.parse(args)
            ok (fn).raises(CommandOptionError, "--file:hom.txt: invalid option.")

        @test("[!h2olx] raises error when unknown long option.")
        def _(self, parser):
            args = ["--flie=hom.txt"]
            def fn(): parser.parse(args)
            ok (fn).raises(CommandOptionError, "--flie=hom.txt: unknown option.")

        @test("[!funte] raises error when validator returns error message for long option value.")
        def _(self, parser):
            args = ["--indent=one"]
            def fn(): parser.parse(args)
            ok (fn).raises(CommandOptionError, "--indent=one: integer expected.")

        @test("[!ti5pm] converts long option value when converter specified to option definition.")
        def _(self, parser):
            args = ["--date=2000-12-31"]
            optdict = parser.parse(args)
            ok (optdict) == {"date": date(2000, 12, 31)}

        @test("[!x2rbq] operates long option value when operator specified to option definition.")
        def _(self, parser):
            args = ["--include=path1", "--include=path2"]
            optdict = parser.parse(args)
            ok (optdict) == {"include": ["path1", "path2"]}

        @test("[!firba] parses short options with required argument.")
        def _(self, parser):
            args = ["-f", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg2"]
            ok (optdict) == {"file": "arg1"}
            #
            args = ["-hf", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg2"]
            ok (optdict) == {"help": True, "file": "arg1"}
            #
            args = ["-fhomhom.txt", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"file": "homhom.txt"}
            #
            args = ["-hfhomhom.txt", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "file": "homhom.txt"}

        @test("[!sl2jw] raises error when short option requires arg but not specified.")
        def _(self, parser):
            args = ["-hf"]
            def fn(): parser.parse(args)
            ok (fn).raises(CommandOptionError, "-f: argument required.")

        @test("[!786zm] parses short options with optional argument.")
        def _(self, parser):
            args = ["-hi4", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "indent": "4"}
            #
            args = ["-hi", "4", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["4", "arg1", "arg2"]
            ok (optdict) == {"help": True, "indent": True}
            #
            args = ["-i", "-h", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "indent": True}
            #
            args = ["-hi"]
            optdict = parser.parse(args)
            ok (args) == []
            ok (optdict) == {"help": True, "indent": True}

        @test("[!ukp51] parses short options without argument.")
        def _(self, parser):
            args = ["-h", "-v", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "version": True}
            #
            args = ["-hv", "arg1", "arg2"]
            optdict = parser.parse(args)
            ok (args) == ["arg1", "arg2"]
            ok (optdict) == {"help": True, "version": True}
            #
            args = ["-h"]
            optdict = parser.parse(args)
            ok (args) == []
            ok (optdict) == {"help": True}

        @test("[!oftl6] raises error when validator returns error message for short option value.")
        def _(self, parser):
            def fn(): parser.parse(["-ih"])
            ok (fn).raises(CommandOptionError, "-i h: integer expected.")
            #
            def fn(): parser.parse(["-d", "Sunday"])
            ok (fn).raises(CommandOptionError, "-d Sunday: YYYY-MM-DD expected")

        @test("[!9up6o] converts short option value when converter specified to option definition.")
        def _(self, parser):
            args = ["-d", "2000-11-30"]
            optdict = parser.parse(args)
            ok (optdict) == {"date": date(2000, 11, 30)}

        @test("[!dv250] operates short option value when operator specified to option definition.")
        def _(self, parser):
            args = ["-I", "path1", "-I", "path2", "-Ipath3"]
            optdict = parser.parse(args)
            ok (optdict) == {"include": ["path1", "path2", "path3"]}



class funcs_TC(unittest.TestCase):

    def provide_members(self):
        class Member(object):
            def __init__(self, id, name):
                self.id   = id
                self.name = name
        return [
            Member(101, "Haruhi"),
            Member(102, "Mikuru"),
            Member(103, "Yuki"),
        ]


    with subject("find_by()"):

        @test("[!7s015] returns first item in items matching to attr value.")
        def _(self, members):
            member = find_by(members, "id", 102)
            ok (member).attr("id", 102).attr("name", "Mikuru")
            member = find_by(members, "name", "Yuki")
            ok (member).attr("id", 103).attr("name", "Yuki")

        @test("[!75jb1] returns None when nothing matched in items.")
        def _(self, members):
            member = find_by(members, "name", "Kyon")
            ok (member) == None


    with subject("find_index()"):

        @test("[!kr2qn] returns index of first item which satisfies condition.")
        def _(self):
            ret = find_index([10, 20, 30, 40, 50, 60], lambda x: x % 3 == 0)
            ok (ret) == 2

        @test("[!4hn0h] returns -1 if nothing satisfied condition.")
        def _(self):
            ret = find_index([10, 20, 30, 40, 50, 60], lambda x: x % 7 == 0)
            ok (ret) == -1



class Application_TC(unittest.TestCase):

    def provide_app(self):
        app = Application()
        result = []
        #
        @app.action("convert", "convert text into html")
        @app.option("-h, --help",         "show help")
        @app.option("-f, --file=FILE",    "filename")
        @app.option("-i, --indent[=num]", "indent (default 2)",
             validate=lambda val: val is True or val.isdigit() or "integer expected.")
        @app.option("-D, --debug[=level]", "debug level (default 1)",
             validate=[lambda val: val is True or val.isdigit() or "integer expected.",
                       lambda val: 1 <= int(val) <= 3  or "out of range (expected 1..3)."])
        def do_convert(*args, **opts):
            app._result = ("convert", args, opts)
            return 0
        #
        @app.action("history", "show history", alias="hist")
        @app.option("-p",   "print content")
        @app.option("-d, --date=DATE", "date (YYYY-MM-DD)",
                    validate=lambda val: re.match(r'^\d\d\d\d-\d\d-\d\d$', val) or "YYYY-MM-DD expected",
                    convert=lambda val: datetime.strptime(val, '%Y-%m-%d').date())
        def do_history(*args, **opts):
            app._result = ("history", args, opts)
            return 0
        #
        return app


    with subject("#__init__()"):

        @test("[!hte7n] takes command name and description.")
        def _(self):
            app = Application("hello", "print 'Hello world' message")
            ok (app.name) == "hello"
            ok (app.desc) == "print 'Hello world' message"


    with subject("#find_action()"):

        @test("[!6bkoj] returns action object when found.")
        def _(self, app):
            action = app.find_action("convert")
            ok (action) != None
            ok (action.name) == "convert"

        @test("[!73cb0] accepts both action name and alias name.")
        def _(self, app):
            action1 = app.find_action("history")
            action2 = app.find_action("hist")
            ok (action2) != None
            ok (action2).is_(action1)

        @test("[!vhitq] returns None when no action found.")
        def _(self, app):
            ok (app.find_action("test")) == None


    with subject("#action()"):

        @test("[!g8kq7] creates new Action object (with options) and keeps it internally.")
        def _(self):
            app = Application()
            @app.action("hist [N]", "show git history")
            def git_hist(*args, **opts):
                pass
            action = app.find_action("hist")
            ok (action).is_a(Action)
            ok (action.name)   == "hist"
            ok (action.argdef) == "[N]"
            ok (action.desc)   == "show git history"

        @test("[!db73h] returns decorator which creates Action object and append to app object.")
        def _(self):
            app = Application()
            @app.action("hist [N]", "show git history")
            def git_hist(*args, **opts):
                return [args, opts]
            ret = git_hist(10, 20, z=30)
            ok (ret) == [(10, 20), {"z": 30}]

        @test("[!go5an] can take alias name as keyword argument.")
        def _(self):
            app = Application()
            @app.action("history [N]", "show git history", alias="hist")
            def git_histotry(*args, **opts):
                pass
            action = app.find_action("history")
            ok (action.name) == "history"
            ok (action.alias) == "hist"


    with subject("#option()"):

        @test("[!xpj0j] creates new Option object and keeps it internally.")
        def _(self):
            app = Application()
            @app.option("-h, --help",    "show help")
            @app.option("-v, --version", "print version")
            def fn(*args, **opts):
                pass
            ok (app).has_attr('_curr_options')
            ok (app._curr_options).is_a(list).length(2)
            ok (app._curr_options[0]).is_a(Option).attr("short", "h").attr("long", "help").attr("desc", "show help")
            ok (app._curr_options[1]).is_a(Option).attr("short", "v").attr("long", "version").attr("desc", "print version")

        @test("[!jgzmw] returns decorator to set Option objects into function.")
        def _(self):
            app = Application()
            @app.option("-h, --help",    "show help")
            @app.option("-v, --version", "print version")
            def fn(*args, **opts):
                return [args, opts]
            ret = fn(10, 20, z=30)
            ok (ret) == [(10, 20), {"z": 30}]


    with subject("#option_if()"):

        @test("[!a1d1p] same as 'options()' when cond is truthy.")
        def _(self):
            app = Application()
            @app.option("-h, --help",    "show help")
            @app.option_if(True, "-v, --version", "print version")
            def fn(*args, **opts):
                pass
            ok (app).has_attr('_curr_options')
            ok (app._curr_options).is_a(list).length(2)
            ok (app._curr_options[1]).is_a(Option).attr("short", "v").attr("long", "version").attr("desc", "print version")

        @test("[!82rnb] do nothing when cond is falsy.")
        def _(self):
            app = Application()
            @app.option("-h, --help",    "show help")
            @app.option_if(False, "-v, --version", "print version")
            def fn(*args, **opts):
                pass
            ok (app).has_attr('_curr_options')
            ok (app._curr_options).is_a(list).length(1)   ## != 2
            ok (app._curr_options[0]).is_a(Option).attr("long", "help")


    with subject("#run()"):

        @test("[!ebcn8] uses default action name when no action specified.")
        def _(self):
            app = Application("hello", "print hello world", default="test")
            @app.action("test", "run test scripts")
            def do_test():
                called[0] = True
            called = [False]
            #
            ok (called[0]) == False
            ret = app.run()
            ok (called[0]) == True

        @test("[!k0lmj] error when no action name nor default action.")
        def _(self):
            app = Application("hello", "print hello world", default=None)
            @app.action("test", "run test scripts")
            def do_test():
                pass
            #
            def fn(): app.run()
            ok (fn).raises(CommandOptionError, "action name required.")

        @test("[!kngbh] alias name is available as action name.")
        def _(self):
            app = Application("hello", "print hello world")
            @app.action("switch name", "switch current branch", alias="sw")
            def do_switch(name):
                called[0] = name
            called = [False]
            #
            app.run("sw", "master")     # invoke with alias name
            ok (called) == ["master"]

        @test("[!wh6o5] error when unknown action name specified.")
        def _(self):
            app = Application("hello", "print hello world")
            @app.action("test", "run test scripts")
            def do_test():
                pass
            #
            def fn(): app.run("tests")
            ok (fn).raises(CommandOptionError, "tests: unknown action.")

        @test("[!rja97] parses long options of action.")
        def _(self, app):
            argv = ["convert",
                    "--help",             # no arg
                    "--file=file.txt",    # required arg
                    "--indent=4",         # optional arg
                    "--debug",            # optional arg
                    "arg1", "arg2"]
            status = app.run(*argv)
            ok (app._result[0]) == "convert"
            ok (app._result[1]) == ("arg1", "arg2")
            ok (app._result[2]) == {"help": True, "file": "file.txt", "indent": "4", "debug": True}
            ok (status) == 0

        @test("[!ymcnv] parses short options of action.")
        def _(self, app):
            argv = ["convert",
                    "-h",                # no arg
                    "-f", "file.txt",    # required arg
                    "-i4",               # optional arg
                    "-D",                # optional arg
                    "arg1", "arg2"]
            status = app.run(*argv)
            ok (app._result[0]) == "convert"
            ok (app._result[1]) == ("arg1", "arg2")
            ok (app._result[2]) == {"help": True, "file": "file.txt", "indent": "4", "debug": True}
            ok (status) == 0
            #
            argv = ["convert", "-hffile.txt", "arg1", "arg2"]
            status = app.run(*argv)
            ok (app._result[0]) == "convert"
            ok (app._result[1]) == ("arg1", "arg2")
            ok (app._result[2]) == {"help": True, "file": "file.txt"}
            #
            argv = ["convert", "-hi4", "arg1", "arg2"]
            status = app.run(*argv)
            ok (app._result[0]) == "convert"
            ok (app._result[1]) == ("arg1", "arg2")
            ok (app._result[2]) == {"help": True, "indent": "4"}


        def provide_app2(self):
            app2 = Application()
            @app2.action("rename old-name new-name", "copy file")
            def do_rename(old_name, new_name, **opts):
                pass
            @app2.action("move dst files...", "copy file")
            def do_move(dst, *files, **opts):
                pass
            @app2.action("fork branch", "create new branch")
            @app2.option("-h, --help", "show help")
            def do_fork(branch, _=None, help=False):
                pass
            return app2

        @test("[!1yqpi] error when required argument is not specified.")
        def _(self, app2):
            def fn1(): app2.run("rename")
            ok (fn1).raises(CommandOptionError, "argument (old-name) required.")
            def fn2(): app2.run("rename", "old1")
            ok (fn2).raises(CommandOptionError, "argument (new-name) required.")
            def fn3(): app2.run("move")
            ok (fn3).raises(CommandOptionError, "argument (dst) required.")
            def fn4(): app2.run("fork")
            ok (fn4).raises(CommandOptionError, "argument (branch) required.")

        @test("[!8pma3] error when too many arguments specified.")
        def _(self, app2):
            def fn(): app2.run("rename", "name1", "name2", "name3")
            ok (fn).raises(CommandOptionError, "too many arguments.")

        @test("[!4r18r] not raise 'too many arguments' error when action func takes variable length arguments.")
        def _(self, app2):
            def fn(): app2.run("move", "dst1", "file1", "file2", "file3")
            ok (fn).not_raise(CommandOptionError)

        @test("[!2onan] supports optional argument.")
        def _(self):
            app = Application()
            @app.action("dir [directory]", "list files in directory")
            def do_dir(directory=None):
                result.append(directory)
            #
            result = []
            app.run("dir", "/tmp")
            ok (result) == ["/tmp"]
            #
            result = []
            app.run("dir")
            ok (result) == [None]

        @test("[!giakv] regards args after '_' as keyword-only args.")
        def _(self):
            result = []
            app = Application()
            @app.action("example", "test action")
            @app.option("--opt1",  "test option")
            def do_example(arg1, arg2=None, _=None, opt1=10):
                result.append(dict(arg1=arg1, arg2=arg2, _=_, opt1=opt1))
            #
            def fn1(): app.run("example", "aaa", "bbb", "ccc")
            ok (fn1).raises(CommandOptionError, "too many arguments.")
            def fn2(): app.run("example", "--opt1", "aaa", "bbb")
            ok (fn2).not_raise(Exception)


    with subject("#main()"):

        @test("[!i5rr3] uses sys.argv when argv is not passed.")
        def _(self, app):
            original = sys.argv[:]
            try:
                sys.argv[:] = ["hom.py", "history", "-p", "arg1", "arg2"]
                try:
                    app.main()
                except SystemExit as ex:
                    pass
                ok (app._result) == ('history', ('arg1', 'arg2'), {'p': True})
            finally:
                sys.argv[:] = original

        @test("[!5zinc] if action function returns integer, regards it as status code.")
        def _(self, app):
            @app.action("sample", "Sample")
            def do_sample():
                return 9
            try:
                app.main(["test.py", "sample"])
            except SystemExit as ex:
                ok (ex.code) == 9
            else:
                assert False, "SystemExit expected, but not raised"

        @test("[!g2cmn] if action function returns string, prints it to stdout.")
        def _(self, app):
            @app.action("sample", "Sample")
            def do_sample():
                return "Hello"
            with dummy_io() as d_io:
                try:
                    app.main(["test.py", "sample"])
                except SystemExit as ex:
                    pass
            sout, serr = d_io
            ok (str(sout)) == "Hello\n"
            ok (str(serr)) == ""



class App_TC(unittest.TestCase):

    def provide_app(self):
        app = App("hello", "print hello world")
        @app.global_action()
        @app.option("-H, --Help", "show help")
        @app.option("-V, --Version", "print version")
        def do_global(_=None, Help=None, Version=None):
            return dict(Help=Help, Version=Version)
        return app


    with subject("#__init__()"):

        @test("[!k4y6k] 'help' action is registered by default.")
        def _(self, app):
            expected = r"""
hello  - print hello world
Usage:
  hello <action> [<options>] [<args>...]
Actions:
  help       : print help
"""[1:]
            ok (app.run("help")) == expected

        @test("[!v7mut] '-h, --helpo' option is registered by default.")
        def _(self):
            app = App("hello")
            expected = r"""
Usage:
  hello <action> [<options>] [<args>...]
Actions:
  help       : print help
"""[1:]
            ok (app.run("-h")) == expected
            ok (app.run("--help")) == expected

        @test("[!kojiw] '-v, --version' option is registered when version is specified.")
        def _(self):
            app = App("hello")
            ok (app.run("-v")) == "0.0.0"
            ok (app.run("--version")) == "0.0.0"


    with subject("#global_action()"):

        @test("[!n8vnm] registers action as global option handler.")
        def _(self, app):
            ok (app._global_action) != None
            ok (app._global_action.options).is_a(list).length(2)
            ok (app._global_action.options[0].long) == "Help"
            ok (app._global_action.options[1].long) == "Version"


    with subject("#run()"):

        @test("[!13njs] parses global command-line options.")
        def _(self, app):
            ret = app.run("-H")
            ok (ret) == {"Help": True, "Version": None}
            ret = app.run("-V")
            ok (ret) == {"Help": None, "Version": True}
            ret = app.run("-VH")
            ok (ret) == {"Help": True, "Version": True}
            ret = app.run("--Help", "--Version")
            ok (ret) == {"Help": True, "Version": True}

        @test("[!q353n] '-' should be regard as argument, not option.")
        def _(self, app):
            def fn(): app.run("-")
            ok (fn).raises(CommandOptionError, "-: unknown action.")


    with subject("#do_help()"):

        @test("[!8dpon] can accept both action name and alias name.")
        def _(self, app):
            @app.action("history", "show history", alias="hist")
            @app.option("-d, --date=DATE", "date (YYYY-MM-DD)")
            def do_history():
                pass
            #
            expected = r"""
hello history - show history
Usage:
  hello history [options] None
Options:
  -d, --date=DATE               : date (YYYY-MM-DD)
"""[1:]
            ret = app.do_help("history")  # action name
            ok (ret) == expected
            ret = app.do_help("hist")     # alias name
            ok (ret) == expected


    with subject("#help_message()"):

        @test("[!fjnd9] command name and description are displayed in help message.")
        def _(self):
            app = App("hello", "print 'Hello world' message")
            s = app.help_message()
            ok (s).should.startswith("hello  - print 'Hello world' message\n" +
                                     "Usage:\n" +
                                     "  hello ")



if __name__ == '__main__':
    import oktest
    oktest.main()
