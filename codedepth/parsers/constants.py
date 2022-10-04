from re import compile
from os import sep


class Patterns:
    REQUIRE = {
        compile(r"require[ \t]*\(\s*(\"|\')((.|\s)*?)\1\s*\)"): 1  # `require('module')`
    }


class Constants:
    NODE_MODULES_FRAGMENT = sep + "node_modules" + sep
