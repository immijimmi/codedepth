from re import compile


class Patterns:
    require = {
        compile(r"require[ \t]*\(\s*(\"|\')((.|\s)*?)\1\s*\)"): 1  # `require('module')`
    }
