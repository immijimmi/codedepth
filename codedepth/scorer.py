from os import path, walk

from .parsers import PyImportParser


class Scorer:
    def __init__(self, dir_path, filters=(), sorters=(), use_parser_filters=True):
        self._dir_path = path.abspath(dir_path)
        # Filtered files do not increment the score of any dependency trees they are in, and are excluded from output
        self._filters = set(filters)
        self.sorters = [*sorters]  # This can be public, because changes after instantiation will not affect the data

        self._import_parsers = [PyImportParser]
        if use_parser_filters:
            for parser in self._import_parsers:
                for func in parser.FILTERS:
                    self._filters.add(func)

        self._scores = {}
        self._connections = {}

    @property
    def dir_path(self):
        return self._dir_path

    @property
    def scores(self):
        result = {}

        for key, value in self._scores.items():
            if all(func(key) for func in self._filters):
                result.update({key: value})

        return result

    @property
    def score_items(self):
        result = self.scores.items()

        for func in self.sorters:
            result = sorted(result, key=func)

        return result

    @property
    def connections(self):
        result = {}
        working_result = self._connections

        changes_made = True
        while changes_made:
            changes_made = False

            for parent, children in working_result.items():
                if self.is_valid_file(parent):
                    updated_children = set()

                    for child in children:
                        if self.is_valid_file(child):
                            updated_children.add(child)
                        else:
                            changes_made = True

                            for nested_child in self._connections[child]:
                                updated_children.add(nested_child)
                else:
                    changes_made = True  # Entry was filtered out of the result via omission

            working_result = {**result}

        return result

    def get_all(self):
        for _path, subdirs, files in walk(self._dir_path):
            for name in files:
                file_path = path.join(_path, name)
                try:
                    self.get_score(file_path)
                except ValueError:
                    pass

        return self.scores

    def get_score(self, file_path):
        file_path = path.abspath(file_path)

        # Preliminary checks
        if file_path[:len(self._dir_path)] != self._dir_path:
            raise ValueError("the file must be located in the specified directory")
        if file_path in self._scores:
            return self._scores[file_path]

        valid_parsers = list(filter(lambda parser: parser.can_parse(file_path), self._import_parsers))
        if not valid_parsers:
            raise ValueError("unable to parse provided file")
        valid_parser = valid_parsers[0]

        try:
            with open(file_path) as file:
                contents = file.read()
        except FileNotFoundError:  # Primarily used to weed out builtins
            raise ValueError("the file must be located in the specified directory")

        dependencies_paths = valid_parser.get_dependencies_paths(contents, path.dirname(file_path))

        score = 0
        for dependency_path in dependencies_paths:
            do_increment_score = self.is_valid_file(dependency_path)  # Filtered files do not increment score

            try:
                dependency_score = self.get_score(dependency_path)
                score = max(score, dependency_score+do_increment_score)

                self._connections[file_path] = self._connections.get(file_path, []) + [dependency_path]
            except ValueError:
                pass

        self._scores[file_path] = score
        return score

    def is_valid_file(self, file_path):
        return all(func(file_path) for func in self._filters)
