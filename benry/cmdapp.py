# -*- coding: utf-8 -*-

###
### $Release: 0.0.0 $
### $Copyright: copyright(c) 2015 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

"""
Library to create command-line application.

Example script (filename: 'myhello')::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    ## create application object
    from benry.cmdapp import App, error
    app = App("myhello", "example script", version="0.0.0")
    action = app.action
    option = app.option

    ## register sub-command
    @action("hello [name]", "print hello world")
    @option("-i, --indent[=N]", "indent width (default 0)",
            validation=lambda val: (
                not val.isdigit() and "integer expected"
                or int(val) <= 0 and "positive value expected"
            ))
    def do_hello(name='world', _=None, indent=0):
        indent = int(indent)
        msg = "Hello %s!" % name
        if indent:
          msg = " " * indent + msg
        print(msg)

    if __name__ == '__main__':
        app.main()

Usage example::

    $ chmod a+x ./myhello
    $ ./myhello help            # list all actions
    $ ./myhello help hello      # show help of 'hello' action
    $ ./myhello --help          # same as ./myhello help
    $ ./myhello                 # same as ./myhello help
    $ ./myhello hello           # run 'hello' action
    $ ./myhello hello -i4 John  # run with option and argument

"""

__version__ = "$Release: 0.0.0 $".split()[1]
__all__ = (
    'App', 'Application', 'SimpleApp', 'OptionParser', 'Action', 'Option',
    'error', 'CommandOptionError', 'OptionDefinitionError',
)

import sys, os, re
python2 = sys.version_info[0] == 2
python3 = sys.version_info[0] == 3

ENCODING = 'utf-8'

if python3:
    _string = (str,)
    _func_defaults = lambda func: func.__defaults__
    def _B(string, encoding=None):
        if isinstance(string, bytes):
            return string
        if not isinstance(string, str):
            string = str(string)
        return string.encode(encoding or ENCODING)
    xrange = range
if python2:
    _string = (str, unicode)
    _func_defaults = lambda func: func.func_defaults
    def _B(string, encoding=None):
        if isinstance(string, str):
            return string
        if isinstance(string, unicode):
            return string.encode(encoding or ENCODING)
        return str(string)


def find_by(items, attr, value):
    #; [!7s015] returns first item in items matching to attr value.
    for item in items:
        if getattr(item, attr) == value:
            return item
    #; [!75jb1] returns None when nothing matched in items.
    return None


def find_index(items, cond):
    #; [!kr2qn] returns index of first item which satisfies condition.
    for i, x in enumerate(items):
        if cond(x):
            return i
    #; [!4hn0h] returns -1 if nothing satisfied condition.
    return -1


def func_has_variable_length_argument(func):
    # https://docs.python.org/3.5/reference/datamodel.html
    # > bit 0x04 is set if the function uses the *arguments syntax
    # > to accept an arbitrary number of positional arguments;
    return func.__code__.co_flags & 0x04


class Application(object):
    """Command-line application."""

    def __init__(self, name=None, desc=None, _=None, default=None):
        self.name = name
        self.desc = desc
        self.default = default
        self._action_list = []
        self._curr_options = []
        self._curr_func    = None
        self._curr_action  = None

    def _register(self, action):
        self._action_list.append(action)

    def find_action(self, name):
        #; [!6bkoj] returns action object when found.
        #; [!73cb0] accepts both action name and alias name.
        #; [!vhitq] returns None when no action found.
        return find_by(self._action_list, 'name', name) or \
               find_by(self._action_list, 'alias', name)

    def action(self, cmddef, desc, _=None, alias=None):
        #; [!db73h] returns decorator which creates Action object and append to app object.
        #; [!go5an] can take alias name as keyword argument.
        def deco(func):
            #; [!g8kq7] creates new Action object (with options) and keeps it internally.
            options = self._curr_options
            self._curr_options = []
            action = Action.new(cmddef, desc, func, options, alias=alias)
            self._register(action)
            return func
        return deco

    def option(self, optdef, desc, _=None, argtype=None, validation=None, conversion=None, operation=None):
        #; [!xpj0j] creates new Option object and keeps it internally.
        option = Option.new(optdef, desc, argtype=argtype, validation=validation,
                            conversion=conversion, operation=operation)
        self._curr_options.append(option)
        #; [!jgzmw] returns decorator to set Option objects into function.
        def deco(func):
            return func
        return deco

    def option_if(self, cond, *args, **kwargs):
        #; [!a1d1p] same as 'options()' when cond is truthy.
        if cond:
            return self.option(*args, **kwargs)
        #; [!82rnb] do nothing when cond is falsy.
        else:
            return lambda func: func

    def main(self, argv=None):
        #; [!i5rr3] uses sys.argv when argv is not passed.
        if argv is None:
            argv = sys.argv
        args = argv[1:]
        #;
        status = 0
        try:
            ret = self._run(args)
        except CommandOptionError as ex:
            if self._curr_action:
                sys.stderr.write("%s %s: " % (self.script_name, self._curr_action.name))
            else:
                sys.stderr.write("%s: " % (self.script_name,))
            sys.stderr.write("%s\n" % (ex,))
            status = 1
        else:
            #; [!5zinc] if action function returns integer, regards it as status code.
            if isinstance(ret, int):
                status = ret
            #; [!g2cmn] if action function returns string, prints it to stdout.
            elif isinstance(ret, _string):
                if python3:
                    output = ret
                elif python2:
                    output = _B(ret)
                print(output)
        sys.exit(status)

    def run(self, *args):
        return self._run(list(args))

    def _run(self, args):
        #; [!ebcn8] uses default action name when no action specified.
        action_name = args.pop(0) if args else self.default
        #; [!k0lmj] error when no action name nor default action.
        if not action_name:
            error("action name required.")
        #; [!kngbh] alias name is available as action name.
        #; [!wh6o5] error when unknown action name specified.
        action = self.find_action(action_name)  or \
            error("%s: unknown action." % action_name)
        self._curr_action = action
        #; [!rja97] parses long options of action.
        #; [!ymcnv] parses short options of action.
        optdict = self._parse_options(args, action.options)
        errmsg = self._validate_args(action.func, args)
        if errmsg:
            #error("%s: %s" % (action.name, errmsg))
            error(errmsg)
        output = action.func(*args, **optdict)
        return output

    def _parse_options(self, args, optdefs):
        return OptionParser(optdefs).parse(args)

    def _validate_args(self, func, args):
        #; [!giakv] regards args after '_' as keyword-only args.
        idx = find_index(func.__code__.co_varnames, lambda x: x == '_')
        arg_count_max = (idx if idx >= 0 else func.__code__.co_argcount)
        #; [!8pma3] error when too many arguments specified.
        if len(args) > arg_count_max:
            #; [!4r18r] not raise 'too many arguments' error when action func takes variable length arguments.
            if not func_has_variable_length_argument(func):
                return "too many arguments."
        #; [!1yqpi] error when required argument is not specified.
        arg_defaults = _func_defaults(func) or ()
        arg_count_min = func.__code__.co_argcount - len(arg_defaults)
        if len(args) < arg_count_min:
            arg_name = func.__code__.co_varnames[len(args)]
            return "argument (%s) required." % arg_name.replace('_', '-')
        #
        return None

    @property
    def script_name(self):
        return self.name or os.path.basename(sys.argv[0])


class App(Application):

    def __init__(self, name=None, desc=None, _=None, default="help", version="0.0.0"):
        Application.__init__(self, name, desc, default=default)
        self.version = version
        self._global_action = None
        #
        self._register_help_action()
        self._register_global_options()

    def _register_help_action(self):
        #; [!k4y6k] 'help' action is registered by default.
        @self.action("help [action]", "print help")
        def do_help(action=None, **opts):
            return self.do_help(action, **opts)

    def _register_global_options(self):
        #; [!v7mut] '-h, --helpo' option is registered by default.
        #; [!kojiw] '-v, --version' option is registered when version is specified.
        @self.global_action()
        @self.option("-h, --help", "help")
        @self.option_if(self.version, "-v, --version", "version")
        def do_global_action(**opts):
            if opts.get('help'):
                return self.run("help")
            elif opts.get('version'):
                return self.version

    def global_action(self):    # TODO: rename to better name
        #; [!n8vnm] registers action as global option handler.
        def deco(func):
            options = self._curr_options
            self._curr_options = []
            self._global_action = Action(None, None, None, func, options)
            return func
        return deco

    def _run(self, args):    # override
        #; [!13njs] parses global command-line options.
        #; [!q353n] '-' should be regard as argument, not option.
        if args and args[0].startswith("-") and args[0] != "-":
            action = self._global_action
            optdict = self._parse_options(args, action.options)
            output = action.func(*args, **optdict)
            return output
        #
        return Application._run(self, args)

    def do_help(self, action_name=None, **opts):
        #; [!8dpon] can accept both action name and alias name.
        if action_name:
            action = self.find_action(action_name)  or \
                error("%s: unknown action name." % action_name)
            help_msg = action.help_message(self.script_name)
        else:
            help_msg = self.help_message()
        return help_msg

    def help_message(self):
        #; [!fjnd9] command name and description are displayed in help message.
        buf = []; add = buf.append
        script_name = self.script_name
        if self.desc:
            add("%s  - %s\n" % (script_name, self.desc))
            add("\n")
        width = self._preferred_width()
        format = "  %-" + str(width) + "s : %s\n"
        add("Usage:\n")
        add("  %s <action> [<options>] [<args>...]\n" % script_name)
        add("\n")
        add("Actions:\n")
        size = len(buf)
        for x in sorted(self._action_list, key=lambda x: x.name):
            if x.desc:
                add(format % (x.name, x.desc))
        if size == len(buf):
            buf.pop()         # remove "Actions:\n"
        return "".join(buf)

    def _preferred_width(self, max_width=25, min_width=10):
        if self._action_list:
            max_len = max( len(x.name) for x in self._action_list )
            max_width = min(max_len, max_width)
        width = max(max_width, min_width)
        return width


class SimpleApp(Application):
    """Application class without actions."""

    def __init__(self, name=None, desc=None):
        #; [!qb6e4] 'default' argument is not available.
        Application.__init__(self, name, desc, default="<action>")

    def action(self, *args, **kwargs):
        #; [!lfjdq] raises error because not available.
        raise OptionDefinitionError("Use @app() instead of @app.action() for SimpleApp class.")

    def __call__(self, argdef=None):
        #; [!nfgyx] same as '@app.action("<action> argdef", desc)'.
        cmddef = "%s %s" % (self.default, argdef or "")
        return Application.action(self, cmddef, self.desc)

    def _run(self, args):
        #; [!960mf] raises error when '@app()' is not called yet.
        action = self.find_action(self.default)
        if action is None:
            raise OptionDefinitionError("@app() should be called before app.main().")
        #; [!tij3s] runs without action name.
        optdict = self._parse_options(args, action.options)
        errmsg = self._validate_args(action.func, args)
        if errmsg:
            error(errmsg)
        output = action.func(*args, **optdict)
        return output

    def help_message(self, _=None, width=30, indent=2, sep=': '):
        #; [!4uki2] builds help message and returns it.
        action = self.find_action(self.default)
        return action.help_message(self.script_name, width=width, indent=indent, sep=sep, print_action=False)


class OptionParser(object):
    """Command-option parser."""

    def __init__(self, optdefs):
        self._optdefs = optdefs

    def _find_by_long(self, long):
        return find_by(self._optdefs, 'long', long)

    def _find_by_short(self, short):
        return find_by(self._optdefs, 'short', short)

    def parse(self, args):
        optdict = {}
        #; [!5eerp] '-' should be regard as argument, not option string.
        while args and args[0].startswith("-") and args[0] != "-":
            optstr = args.pop(0)
            #; [!ugy1h] stops to parse action options when arg is '--'.
            if optstr == "--":
                break
            #; [!vmcdf] parses long options of action.
            elif optstr.startswith("--"):
                self._parse_long_option(optstr, args, optdict)
            #; [!b6178] parses short options of action.
            else:
                self._parse_short_option(optstr, args, optdict)
        return optdict

    def _parse_long_option(self, optstr, args, optdict):
        assert optstr.startswith("--")
        #; [!tzuoh] raises error when invalid format long option.
        m = re.match('^--(\w[-\w]*)(?:=(.*))?$', optstr)  or \
            error("%s: invalid option." % optstr)
        optname, optval = m.groups()
        #; [!h2olx] raises error when unknown long option.
        optdef = self._find_by_long(optname)  or \
            error("%s: unknown option." % optstr)
        #; [!ktzbb] raises error when long option requires arg but not specified.
        if optdef.arg_required is True:
            optval is not None  or error("%s: argument required." % optstr)
        #; [!mzzd4] raises error when long option doesn't require arg but specified.
        elif optdef.arg_required is None:
            optval is None  or error("%s: unexpected argument." % optstr)
        if optval is None:
            optval = True
        #; [!funte] raises error when validator returns error message for long option value.
        #; [!ti5pm] converts long option value when converter specified to option definition.
        optval, errmsg = optdef.handle_value(optval)
        if errmsg:
            error("%s: %s" % (optstr, errmsg))
        #; [!x2rbq] operates long option value when operator specified to option definition.
        if optdef.operation:
            optdef.operation(optval, optdict)
        else:
            optdict[optdef.name] = optval

    def _parse_short_option(self, optstr, args, optdict):
        assert optstr.startswith("-")
        i = 1       # ignore first '-' character
        length = len(optstr)
        while i < length:
            optch = optstr[i]
            optdef = self._find_by_short(optch)  or \
                error("-%s: unknown option." % optch)
            #; [!firba] parses short options with required argument.
            if optdef.arg_required == True:
                i += 1
                if i == length:
                    #; [!sl2jw] raises error when short option requires arg but not specified.
                    args  or error("-%s: argument required." % optch)
                assert i <= length
                optval = (args.pop(0) if i == length else
                          optstr[i:]  if i <  length else None)
                i = length
            #; [!786zm] parses short options with optional argument.
            elif optdef.arg_required == False:
                i += 1
                assert i <= length
                optval = (True       if i == length else
                          optstr[i:] if i <  length else None)
                i = length
            #; [!ukp51] parses short options without argument.
            else:
                i += 1
                optval = True
            #; [!oftl6] raises error when validator returns error message for short option value.
            #; [!9up6o] converts short option value when converter specified to option definition.
            optval, errmsg = optdef.handle_value(optval)
            if errmsg:
                if optval is True: error("-%s: %s" % (optch, errmsg))
                else:              error("-%s %s: %s" % (optch, optval, errmsg))
            #; [!dv250] operates short option value when operator specified to option definition.
            if optdef.operation:
                optdef.operation(optval, optdict)
            else:
                optdict[optdef.name] = optval
        #
        return optdict


class CommandOptionError(Exception):
    """Represents command-line option is wrong."""
    pass


def error(msg):
    raise CommandOptionError(msg)


class Action(object):
    """Action definition."""

    def __init__(self, name, argdef, desc, func, options, alias=None):
        self.name    = name
        self.argdef  = argdef
        self.desc    = desc
        self.func    = func
        self.options = options
        self.alias   = alias

    @classmethod
    def new(cls, defstr, desc, func, opts, alias=None):
        #; [!3g317] parses action definition string.
        name, argdef = cls.parse(defstr)
        #; [!rf00z] returns new Action object.
        return cls(name, argdef, desc, func, opts, alias=alias)

    @staticmethod
    def parse(defstr):
        #; [!e9psb] strips action definition string.
        defstr = defstr.strip()
        #; [!pe0b5] parses string, and returns action name and argument definition.
        pair = re.split(r'\s+', defstr, 1)
        if len(pair) == 1:
            name, argdef = pair[0], None
        elif len(pair) == 2:
            name, argdef = pair
            argdef = argdef.strip()
        return name, argdef

    def __call__(self, *args, **kwargs):
        #; [!tm64g] invokes func with arguments.
        return self.func(*args, **kwargs)

    def help_message(self, script_name, width=30, indent=2, sep=': ', print_action=True):
        buf = []; add = buf.append
        #; [!rmrd7] don't print action when print_action arg is falthy.
        action_str = " " + self.name if print_action else ""
        #; [!zohvj] includes script name, action name and description.
        #; [!iqqaw] don't print script nor action name when description is None.
        if self.desc is not None:
            add("%s%s - %s\n" % (script_name, action_str, self.desc))
        #; [!98tyn] adds document if function has it.
        func_doc = self.format_funcdoc(indent=indent)
        if func_doc:
            add(self.format_funcdoc(indent=indent))
        #; [!e8ps2] includes usage of action.
        options_doc = self.format_options(width=width, indent=indent, sep=sep)
        if buf:
            add("\n")
        add("Usage:\n")
        add("%s%s%s%s%s\n" % (" " * indent, script_name, action_str,
                              " [<options>]" if options_doc else "",
                              " "+self.argdef if self.argdef else ""))
        #; [!kb62s] includes help message of options.
        if options_doc:
            add("\n")
            add("Options:\n")
            add(options_doc)
        #; [!ccl90] returns help message of action.
        return "".join(buf)

    def format_options(self, width=30, indent=2, sep=': '):
        #; [!s2ip2] returns command-option help string.
        format = (" " * indent) + "%-" + str(width) + "s" + sep + "%s\n"
        text = "".join( format % (opt.format(), opt.desc)
                            for opt in self.options if opt.desc )
        return text

    def format_funcdoc(self, indent=2):
        doc = self.func.__doc__
        if not doc:
            return ""
        if doc.startswith("\n"):
            doc = doc[1:]
        doc = re.sub(r"\n\s+$", "\n", doc)
        if not doc.endswith("\n"):
            doc += "\n"
        m = re.compile(r'^([ \t]+)', re.M).search(doc)
        original_indent = m.group(1) if m else ""
        doc = re.compile(r'^'+original_indent, re.M).sub(" " * indent, doc)
        return doc


class Option(object):
    """Definition of command line option, not actual option value."""

    def __init__(self, short, long, desc, canonical=None,
                 arg_name=None, arg_required=None, arg_type=None,
                 validation=None, conversion=None, operation=None):
        self.short = short
        self.long  = long
        self.desc  = desc
        self.canonical = canonical
        self.arg_name     = arg_name
        self.arg_required = arg_required
        self.arg_type     = arg_type
        self.validation   = validation
        self.conversion   = conversion
        self.operation    = operation

    @property
    def name(self):
        return self.canonical or self.long or self.short

    def __repr__(self):
        attrs = ('short', 'long', 'canonical', 'desc',
                 'arg_name', 'arg_required', 'arg_type',
                 'validation', 'conversion', 'action')
        buf = ["<", self.__class__.__name__]
        for k in attrs:
            v = getattr(self, k)
            if v is not None:
                buf.append(" %s=%r" % (k, v))
        buf.append(">")
        return "".join(buf)

    @classmethod
    def new(cls, optdef, desc, argtype=None, validation=None, conversion=None, operation=None):
        #; [!8s9ue] parses option definition string.
        tupl = cls.parse(optdef)
        short, long, arg_name, arg_required = tupl
        #; [!k25na] returns new Option object.
        return cls(short, long, desc,
                   arg_name=arg_name, arg_required=arg_required, arg_type=argtype,
                   validation=validation, conversion=conversion, operation=operation)

    @staticmethod
    def parse(optdef):
        #; [!0ifmd] strips option definition string.
        optdef = optdef.strip()
        #; [!yxg3b] parses both short and long option defstr.
        m = re.match(r'^-(\w),\s+--(\w[-\w]*)(?:=(.+)|\[=(.+)\])?$', optdef)
        if m:
            short, long, arg1, arg2 = m.groups()
            required = True if arg1 else False if arg2 else None
            return short, long, arg1 or arg2, required
        #; [!z51ip] parses short options defstr.
        m = re.match(r'^-(\w)(?:\s+(.+)|\[(.+)\])?$', optdef)
        if m:
            short, arg1, arg2 = m.groups()
            required = True if arg1 else False if arg2 else None
            return short, None, arg1 or arg2, required
        #; [!70euy] parses long option defstr.
        m = re.match(r'^--(\w[-\w]*)(?:=(.+)|\[=(.+)\])?$', optdef)
        if m:
            long, arg1, arg2 = m.groups()
            required = True if arg1 else False if arg2 else None
            return None, long, arg1 or arg2, required
        #; [!5nqu9] raises OptionDefinitionError when invalid option definition string.
        raise OptionDefinitionError("%s: invalid option definition." % optdef)

    def handle_value(self, optval):
        if self.validation:
            if isinstance(self.validation, (tuple, list)):
                validators = self.validation
            else:
                validators = [self.validation]
            for fn in validators:
                errmsg = fn(optval)
                if isinstance(errmsg, _string):
                    return optval, errmsg
        if self.conversion:
            optval = self.conversion(optval)
        return optval, None

    def format(self):
        #; [!dljh9] returns string such as '-h, --help' when option takes no arg.
        #; [!je9ya] returns string such as '-f, --file=FILE' when option takes required arg.
        #; [!s49hx] returns string such as '-i, --indent[=N]' when optoin takes optional arg.
        idx = (0  if not self.arg_name else
               1  if self.arg_required else
               2)
        formats = self._FORMATS
        format = (formats[idx][2]  if self.short and self.long else
                  formats[idx][0]  if self.short               else
                  formats[idx][1]  if self.long                else
                  None)
        assert format is not None, "unreachable"
        return format.format(short=self.short, long=self.long, arg=self.arg_name)

    _FORMATS = (
        ("-{short}",        "    --{long}",         "-{short}, --{long}"),
        ("-{short} {arg}",  "    --{long}={arg}",   "-{short}, --{long}={arg}"),
        ("-{short}[{arg}]", "    --{long}[={arg}]", "-{short}, --{long}[={arg}]"),
    )


class OptionDefinitionError(Exception):
    pass
