# -*- coding: utf-8 -*-

__all__ = (
    'App', 'Application', 'OptionParser', 'Action', 'Option',
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
        self.actions = []
        self.default = default
        self._curr_options = []
        self._curr_func    = None
        self._curr_action  = None

    def _register(self, action):
        self.actions.append(action)

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

    def option(self, optdef, desc, _=None, argtype=None, validate=None, convert=None, operate=None):
        #; [!xpj0j] creates new Option object and keeps it internally.
        option = Option.new(optdef, desc, argtype=argtype, validate=validate,
                            convert=convert, operate=operate)
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
        action = find_by(self.actions, "name", action_name)  or \
                 find_by(self.actions, "alias", action_name)  or \
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
        arg_count_min = arg_count_max - len(arg_defaults)
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
        if args and args[0].startswith("-"):
            action = self._global_action
            optdict = self._parse_options(args, action.options)
            output = action.func(*args, **optdict)
            return output
        #
        return Application._run(self, args)

    def do_help(self, action_name=None, **opts):
        #; [!8dpon] can accept both action name and alias name.
        if action_name:
            action = find_by(self.actions, 'name', action_name)  or \
                     find_by(self.actions, 'alias', action_name)  or \
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
        width = self._preferred_width()
        format = "  %-" + str(width) + "s : %s\n"
        add("Usage: %s <action> [<options>] [<args>...]\n" % script_name)
        add("Actions:\n")
        for x in sorted(self.actions, key=lambda x: x.name):
            if x.desc:
                add(format % (x.name, x.desc))
        return "".join(buf)

    def _preferred_width(self, max_width=25, min_width=10):
        if self.actions:
            max_len = max( len(x.name) for x in self.actions )
            max_width = min(max_len, max_width)
        width = max(max_width, min_width)
        return width


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
        while args and args[0].startswith("-"):
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
        if optdef.operate:
            optdef.operate(optval, optdict)
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
            if optdef.operate:
                optdef.operate(optval, optdict)
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

    def help_message(self, script_name, width=30, indent=2, sep=': '):
        buf = []; add = buf.append
        add("%s %s - %s\n" % (script_name, self.name, self.desc))
        add("Usage:\n")
        if self.options:
            add("  %s %s [options] %s\n" % (script_name, self.name, self.argdef))
            add("Options:\n")
            add(self.format_options(width=width, indent=indent, sep=sep))
        else:
            add("  %s %s %s\n" % (script_name, self.name, self.argdef))
        return "".join(buf)

    def format_options(self, width=30, indent=2, sep=': '):
        #; [!s2ip2] returns command-option help string.
        format = (" " * indent) + "%-" + str(width) + "s" + sep + "%s\n"
        text = "".join( format % (opt.format(), opt.desc)
                            for opt in self.options if opt.desc )
        return text


class Option(object):
    """Definition of command line option, not actual option value."""

    def __init__(self, short, long, desc, canonical=None,
                 arg_name=None, arg_required=None, arg_type=None,
                 validate=None, convert=None, operate=None):
        self.short = short
        self.long  = long
        self.desc  = desc
        self.canonical = canonical
        self.arg_name     = arg_name
        self.arg_required = arg_required
        self.arg_type     = arg_type
        self.validate     = validate
        self.convert      = convert
        self.operate      = operate

    @property
    def name(self):
        return self.canonical or self.long or self.short

    def __repr__(self):
        attrs = ('short', 'long', 'canonical', 'desc',
                 'arg_name', 'arg_required', 'arg_type',
                 'validate', 'convert', 'action')
        buf = ["<", self.__class__.__name__]
        for k in attrs:
            v = getattr(self, k)
            if v is not None:
                buf.append(" %s=%r" % (k, v))
        buf.append(">")
        return "".join(buf)

    @classmethod
    def new(cls, optdef, desc, argtype=None, validate=None, convert=None, operate=None):
        #; [!8s9ue] parses option definition string.
        tupl = cls.parse(optdef)
        short, long, arg_name, arg_required = tupl
        #; [!k25na] returns new Option object.
        return cls(short, long, desc,
                   arg_name=arg_name, arg_required=arg_required, arg_type=argtype,
                   validate=validate, convert=convert, operate=operate)

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
        if self.validate:
            if isinstance(self.validate, (tuple, list)):
                validators = self.validate
            else:
                validators = [self.validate]
            for fn in validators:
                errmsg = fn(optval)
                if isinstance(errmsg, _string):
                    return optval, errmsg
        if self.convert:
            optval = self.convert(optval)
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
