import os
import sys
import ast
import yaml
import glob
import argparse
import functools
import importlib
from copy import deepcopy
from itertools import product


def to_flat_dict(d, delim='.', copy=True):
    """TLDR;
    While there are entries in the dictionary that have a dict as a value:
        pop them at the outer level and create a delimitted path as a key, eg:
            {'a': {'b': {'c': 0}}} -> {'a.b': {'c': 0}}
            # by same process
            {'a.b': {'c': 0}} -> {'a.b.c': 0}
    """
    flat = dict(d) if copy else d
    incomplete = list(flat)
    while(incomplete):
        k = incomplete.pop()
        if isinstance(flat[k], dict):
            val = flat.pop(k)
            for subk, subv in val.items():
                new_key = delim.join((k, subk))
                flat[new_key] = subv
                incomplete.append(new_key)
    return flat


def to_nested_dict(d, delim='.', copy=True):
    """TLDR;

    flat: {"a.b.c":0}
    # pop 'a.b.c' and value 0 and break key into parts
    parts:  ['a','b','c']:

    # process 'a'
    flat <- {'a':dict()}
    # process 'b'
    flat <- {'a': {'b': dict()}}
    # process 'c' @ tmp[parts[-1]] = val
    flat <- {'a': {'b': {'c': 0}}}

    """
    flat = dict(d) if copy else d
    keys = list(d) # we copy the keys since we are modifying the dict in place
    for key in keys:
        # Basic idea: for all keys that contain the delim
        if delim in key:
            val = flat.pop(key)
            # get the parts (a.b.c -> [a, b, c])
            parts = key.split(delim)
            # we start with the outer dict, but as we process parts of the key
            level = flat # we assign level to the newly created deeper dicts
            for part in parts[:-1]:
                if part not in level:    # if the part isn't a key at this depth
                    level[part] = dict() # create a new dict to fill
                level = level[part]      # go deeper into the dict
            level[parts[-1]] = val # when we get to the "leaf" set it as val
    return flat


def parse_values(l):
    return [parse_value(e) for e in l]


def parse_value(v):
    try:
        return ast.literal_eval(str(v))
    except Exception:
        return str(v)


def get_deep_attr(obj, key, delim='.'):
    parts = key.split(delim)
    return functools.reduce(lambda x, y: getattr(x, y), parts, obj)


def set_deep_attr(obj, key, val, delim='.'):
    parts = key.split(delim)
    if len(parts) > 1:
        prefix = delim.join(parts[:-1])
        ending = parts[-1]
        setattr(get_deep_attr(obj, prefix, delim=delim),
                ending,
                val)
    else:
        # This was a shallow setattr
        setattr(obj, key, val)


def dict_from_file(filename):
    with open(filename, 'r') as f:
        d = yaml.safe_load(f.read())
    return d


def flat_dict_from_file(filename, delim='.'):
    return to_flat_dict(dict_from_file(filename), delim=delim)


class ArgumentParser(argparse.ArgumentParser):
    """Wrapper of argparse.ArgumentParser that exposes a dotable
    Blueprint object instead of the default Namespace object."""

    def __init__(self, **kwargs):

        formatter_class = kwargs.pop('formatter_class',
                                     MLHelpFormatter)
        allow_abbrev = kwargs.pop('allow_abbrev', False)
        usage = kwargs.pop('usage', None)
        # allow_abbrev is new in version 3.5
        # if older we can't disable it :(
        if sys.version_info[:2] < (3, 5):
            super(ArgumentParser, self).__init__(
                    formatter_class=formatter_class,
                    usage=usage,
                    **kwargs)
        else:
            super(ArgumentParser, self).__init__(
                    allow_abbrev=allow_abbrev,
                    formatter_class=formatter_class,
                    usage=usage,
                    **kwargs)

    def parse_args(self, args=None, namespace=None):
        """We use the Namespace usually returned by argparser.parser_args
        to populate a Blueprint. This means that nested attributes are
        accessible using dots:

            bp = parser.parse_args()
            # do stuff with bp.deep.attribute
        """
        sup = super(ArgumentParser, self)
        args = sup.parse_args(args=args, namespace=namespace)
        return Blueprint.from_dict(to_nested_dict(vars(args)))


class MLHelpFormatter(argparse.HelpFormatter):
    """Formatter that prints defaults in help."""

    def _format_action_invocation(self, action):
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar

        else:
            parts = []

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s %s (default: %s)' % (option_string, args_string, action.default))

            return ', '.join(parts)


class YAMLLoaderAction(argparse.Action):
    """Action that can be used with argparse to dynamically create arguments
    with defaults and types based on a yaml file. The user can then override
    these default values as long as he tries to set them after providing
    the path to the yaml file.

    Example:

        myscript.py --arg1 foo --yamlfile dir/conf.yaml --arg_from_yaml bar

    """

    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 help=None,
                 metavar=None,
                 required=True):

        self._choices_actions = []
        help = help or 'YAML file with default settings'
        metavar = metavar or 'BLUEPRINT_FILE [--opt1 val1] [--opt2 val2]'

        super(YAMLLoaderAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=argparse.PARSER,
            choices=None,
            help=help,
            required=required,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        fname = values[0]
        rest = values[1:]

        if not os.path.isfile(fname):
            raise argparse.ArgumentError(argument=self,
            message="Path %s doesn't exist or is not a file" % fname)
        elif not os.access(fname, os.R_OK):
            raise argparse.ArgumentError(argument=self,
                                         message='Path %s cannot be read' % fname)

        conf = flat_dict_from_file(fname)
        my_reprs = ' '.join(self.option_strings)
        if sys.version_info[:2] < (3, 5):
            subparser = argparse.ArgumentParser(formatter_class=MLHelpFormatter,
                    usage=parser.format_usage()[6:], # replace "usage:"
                    description='YAMLLoader action help: info about arguments '
                                'you can pass after %s. For more details on '
                                'global opts use -h or --help before %s.'
                                % (my_reprs, my_reprs))
        else:
            subparser = argparse.ArgumentParser(formatter_class=MLHelpFormatter,
                    usage=parser.format_usage()[6:], # replace "usage:"
                    allow_abbrev=False,
                    description='YAMLLoader action help: info about arguments '
                                'you can pass after %s. For more details on '
                                'global opts use -h or --help before %s.'
                                % (my_reprs, my_reprs))
        for key, val in sorted(conf.items()):
            # bool('False') is true in python, and argparse doesn't
            # bother erroring - or patching this
            tp = type(val)
            if tp == bool:
                tp = lambda v: v.lower() in ('true', '1', 'yes')
            subparser.add_argument('--%s' % key,
                                   default=val,
                                   required=False,
                                   dest=key,
                                   type=tp,
                                   action=argparse._StoreAction,
                                   metavar=type(val).__name__)
        # set blueprint
        setattr(namespace, self.dest, fname)
        # remove this action after dealing with it because otherwise
        # argparse will whine that we haven't completed it
        parser._remove_action(self)

        subnamespace, arg_strings = subparser.parse_known_args(rest, None)
        for key, value in vars(subnamespace).items():
            setattr(namespace, key, value)
        # if we didn't manage to parse everything..
        if arg_strings:
            # NOTE: we only accept options not from yaml before loading
            # the yaml defaults
            raise argparse.ArgumentError(argument=self,
            message='Unknown settings. Trying to set %r after using '
                    'YAMLLoaderAction. If these are settings for the main '
                    'part of the script, please set such keys before %s.'
                    % (arg_strings, self.option_strings[0]))


class YAMLGridSearchAction(argparse.Action):
    """Action that can be used with argparse to dynamically create arguments
    with defaults and types based on a yaml file. The user can then override
    these default values as long as he tries to set them after providing
    the path to the yaml file.

    Example:

        myscript.py --arg1 foo --yamlfile dir/conf.yaml --arg_from_yaml bar

    """

    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 help=None,
                 metavar=None,
                 required=True):

        self._choices_actions = []
        help = help or 'YAML file with default settings'
        metavar = metavar or 'BLUEPRINT_FILE [--opt1 val1] [--opt2 val2]'

        super(YAMLGridSearchAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=argparse.PARSER,
            choices=None,
            help=help,
            required=required,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        fname = values[0]
        rest = values[1:]

        if not os.path.isfile(fname):
            raise argparse.ArgumentError(argument=self,
            message="Path %s doesn't exist or is not a file" % fname)
        elif not os.access(fname, os.R_OK):
            raise argparse.ArgumentError(argument=self,
            message='Path %s cannot be read' % fname)

        conf = flat_dict_from_file(fname)
        my_reprs = ' '.join(self.option_strings)
        if sys.version_info[:2] < (3, 5):
            subparser = argparse.ArgumentParser(formatter_class=MLHelpFormatter,
                    usage=parser.format_usage()[6:], # replace "usage:"
                    description='YAMLLoader action help: info about arguments '
                                'you can pass after %s. For more details on '
                                'global opts use -h or --help before %s.'
                                % (my_reprs, my_reprs))
        else:
            subparser = argparse.ArgumentParser(formatter_class=MLHelpFormatter,
                    usage=parser.format_usage()[6:], # replace "usage:"
                    allow_abbrev=False,
                    description='YAMLLoader action help: info about arguments '
                                'you can pass after %s. For more details on '
                                'global opts use -h or --help before %s.'
                                % (my_reprs, my_reprs))
        for key, val in sorted(conf.items()):
            # bool('False') is true in python, and argparse doesn't
            # bother erroring - or patching this
            tp = type(val)
            if tp == bool:
                tp = lambda v: v.lower() in ('true', '1', 'yes')
            subparser.add_argument('--%s' % key,
                                   default=val,
                                   required=False,
                                   nargs='*',
                                   dest=key,
                                   type=tp,
                                   action=argparse._StoreAction,
                                   metavar=type(val).__name__)
        # set blueprint
        setattr(namespace, self.dest, fname)
        # remove this action after dealing with it because otherwise
        # argparse will whine that we haven't completed it
        parser._remove_action(self)

        subnamespace, arg_strings = subparser.parse_known_args(rest, None)

        conf = Blueprint.from_file(fname)

        grid_search_kvs = dict()
        for key, value in vars(subnamespace).items():
            # If we find that the default value was modified we interpret it
            # as being an iterable of values to grid search over
            default_value = conf[key]
            if value != default_value:
                grid_search_kvs[key] = value

        grid = product(*[parse_values(v)
                         for v in grid_search_kvs.values()])

        blueprints = []
        for setup in grid:
            new_conf = deepcopy(conf)
            for key, val in zip(grid_search_kvs.keys(), setup):
                new_conf[key] = val
            blueprints.append(new_conf)

        setattr(namespace, 'grid_blueprints', blueprints)

        # if we didn't manage to parse everything..
        if arg_strings:
            # NOTE: we only accept options not from yaml before loading
            # the yaml defaults
            raise argparse.ArgumentError(argument=self,
            message='Unknown settings. Trying to set %r after using '
                    'YAMLLoaderAction. If these are settings for the main '
                    'part of the script, please set such keys before %s.'
                    % (arg_strings, self.option_strings[0]))


class Blueprint(object):
    """Container that Implements a dictionary style interface 
    while also allowing dot access. Supports instantiating classes
    that are represented with dictionary entries with _classname and _module 
    entries through reflection. This is especially useful when we don't know
    some parameters a priori."""

    BP_PREFIX = '$'
    MODULE = '%smodule' % BP_PREFIX
    CLASS = '%sclassname' % BP_PREFIX
    # TODO: Implement functions as callables.
    # FUNCTION = '$funcname'
    # in case you must use positional args
    # this may be a bit counter-intuitive
    POSITIONAL = '%spos_args' % BP_PREFIX

    def __init__(self, **kwargs):
        super(Blueprint, self).__init__()
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        contents = yaml.safe_dump(self.as_dict(),
                                  default_flow_style=False,
                                  sort_keys=False)
        contents = contents.replace('\n', '\n  ').rstrip()
        return 'Blueprint:\n  %s' % (contents)

    def __str__(self):
        contents = yaml.safe_dump(self.as_dict(),
                                  default_flow_style=False,
                                  sort_keys=False)
        contents = contents.replace('\n', '\n  ').rstrip()
        return 'Blueprint:\n  %s' % (contents)

    def __iter__(self):
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key):
        try:
            return get_deep_attr(self, key, delim='.')
        except AttributeError:
            raise KeyError('Key: %s not found' % key)

    def __eq__(self, other):
        for key, val in self.__dict__.items():
            if key not in other:
                return False
            if other[key] != val:
                return False
        return True

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def __setitem__(self, key, value):
        return set_deep_attr(self, key, value, delim='.')

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            pass
        return False

    @classmethod
    def _from_dict(cl, obj):
        # named tuple (can't check isinstance)
        if hasattr(obj, '_asdict'):
            # check if this is one of our classes
            clone = obj._asdict()
            for key, val in clone.items():
                obj[key] = cl._from_dict(val)
            return cl(**clone)
            # only replace dicts if we are not inside class params
        elif isinstance(obj, dict):
            # check if this is one of our classes
            for key, val in obj.items():
                obj[key] = cl._from_dict(val)
            return cl(**obj)
        elif isinstance(obj, list):
            obj = [cl._from_dict(val) for val in obj]
        elif isinstance(obj, tuple):
            obj = tuple(cl._from_dict(val) for val in obj)
        return obj

    @classmethod
    def from_dict(cl, obj, copy=True, delim='.'):
        """Recursively wrap dicts into Blueprint to allow . access."""
        if copy:
            clone = deepcopy(obj)
            return cl._from_dict(clone)
        return cl._from_dict(obj)

    @staticmethod
    def _to_dict(obj):
        attrs = getattr(obj, '__dict__', None)
        if attrs:
            classname = obj.__class__.__name__
            module = obj.__class__.__name__
            obj = dict(attrs)
            if classname is not 'Blueprint':
                obj[Blueprint.CLASS] = classname
                obj[Blueprint.MODULE] = module
            # NOTE: may need to revisit below
            # There were cases where these elements included themselves
            # inside __dict__ .. and we got some nice recursions going.
            # may need to avoid recursively calling _to_dict.
            for key, val in attrs.items():
                obj[key] = Blueprint._to_dict(val)
        # named tuple (can't check isinstance)
        elif hasattr(obj, '_asdict'):
            # check if this is one of our classes
            clone = obj._asdict()
            for key, val in clone.items():
                obj[key] = Blueprint._to_dict(val)
            obj = dict(**clone)
            # only replace dicts if we are not inside class params
        elif isinstance(obj, dict):
            # check if this is one of our classes
            for key, val in obj.items():
                obj[key] = Blueprint._to_dict(val)
            obj = dict(**obj)
        elif isinstance(obj, list):
            obj = [Blueprint._to_dict(val) for val in obj]
        elif isinstance(obj, tuple):
            obj = tuple(Blueprint._to_dict(val) for val in obj)
        return obj

    def as_dict(self):
        return Blueprint._to_dict(self)

    def as_flat_dict(self):
        d = Blueprint._to_dict(self)
        return Blueprint.to_path_dict(d, [], dict())

    @staticmethod
    def to_path_dict(obj, stack, completed, delim='.'):
        if isinstance(obj, dict):
            for key, val in obj.items():
                stack.append(key)
                Blueprint.to_path_dict(val, stack, completed)
                stack.pop()
        elif isinstance(obj, (list, tuple)):
            for key, val in enumerate(obj):
                stack.append(str(key))
                Blueprint.to_path_dict(val, stack, completed)
                stack.pop()
        else:
            completed[delim.join(stack)] = obj
        return completed

    def to_file(self, filename):
        d = self.as_dict()
        with open(filename, 'w') as f:
            f.write(yaml.safe_dump(d, sort_keys=False, default_flow_style=False))

    @classmethod
    def from_file(cl, filename):
        d = dict_from_file(filename)
        return cl.from_dict(d)

    @staticmethod
    def build_children(d, verbose):
        attrs = getattr(d, '__dict__', None)
        if attrs:
            if all(attr in attrs.keys() for attr in [Blueprint.MODULE, Blueprint.CLASS]):
                module_name = attrs.pop(Blueprint.MODULE)
                classname = attrs.pop(Blueprint.CLASS)
                pos_args = attrs.pop(Blueprint.POSITIONAL, tuple())
                for key, val in attrs.items():
                    # If we are inside the class params we only
                    # want to allow further class instantiation
                    attrs[key] = Blueprint.build_children(val, verbose)
                module = importlib.import_module(module_name)
                cls = getattr(module, classname)
                if verbose:
                    print('Creating %s with params %s' % (classname, attrs))
                return cls(*pos_args, **attrs)
            else:
                for key, val in attrs.items():
                    # If we are inside the class params we only
                    # want to allow further class instantiation
                    attrs[key] = Blueprint.build_children(val, verbose)
        elif isinstance(d, dict):
            for key, val in d.items():
                d[key] = Blueprint.build_children(val, verbose)
        elif isinstance(d, (list, tuple)):
            d = [Blueprint.build_children(each, verbose) for each in d]
        return d

    def build(self, copy=True, verbose=False):
        """Recursively replace Blueprint instances with instances of classes
        they represent (if they do)."""
        if copy:
            built = deepcopy(self)
            return Blueprint.build_children(built, verbose)
        return Blueprint.build_children(self, verbose)
