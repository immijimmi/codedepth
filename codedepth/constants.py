class Errors:
    class ExternalFileError(FileNotFoundError):
        pass

    class NoValidParserError(NotImplementedError):
        pass
