from re import compile

from ..constants import Constants as ScorerConstants


class Patterns:
    REQUIRE = {
        compile(r"require[ \t]*\(\s*(\"|\')((.|\s)*?)\1\s*\)"): 1  # `require('module')`
    }


class Constants:
    NODE_MODULES_FRAGMENT = ScorerConstants.PATH_DELIMITER + "node_modules" + ScorerConstants.PATH_DELIMITER
