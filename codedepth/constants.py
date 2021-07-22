from os import getcwd


class Errors:
    class ExternalFileError(FileNotFoundError):
        pass

    class NoValidParserError(NotImplementedError):
        pass


class Constants:
    __cwd = getcwd()
    if ("\\" in __cwd) and ("/" in __cwd):
        raise NotImplementedError("unable to work with path which contains both forward and back slashes")
    elif ("\\" not in __cwd) and ("/" not in __cwd):
        raise NotImplementedError("unable to detect whether paths will contain forward or back slashes")
    else:
        path_delimiter = "\\" if "\\" in __cwd else "/"
