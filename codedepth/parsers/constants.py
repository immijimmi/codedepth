from re import compile

from ..constants import Constants as MainConstants


class Patterns:
    require = {
        compile(r"require[ \t]*\(\s*(\"|\')((.|\s)*?)\1\s*\)"): 1  # `require('module')`
    }


class Constants:
    node_modules_fragment = MainConstants.path_delimiter + "node_modules" + MainConstants.path_delimiter
