from re import compile

from ..constants import Constants as MainConstants


class Patterns:
    REQUIRE = {
        compile(r"require[ \t]*\(\s*(\"|\')((.|\s)*?)\1\s*\)"): 1  # `require('module')`
    }


class Constants:
    NODE_MODULES_FRAGMENT = MainConstants.PATH_DELIMITER + "node_modules" + MainConstants.PATH_DELIMITER
