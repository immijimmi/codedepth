from os import path, walk
from networkx import DiGraph, draw_shell as draw
from matplotlib import pyplot

from .parsers import PyImportParser


class ExternalFileError(FileNotFoundError):
    pass


class NoValidParserError(NotImplementedError):
    pass


class Scorer:
    def __init__(self, dir_path, filters=(), sorters=(), use_parser_filters=True):
        self._dir_path = path.abspath(dir_path)
        # Filtered files do not increment the score of any dependency trees they are in, and are excluded from output
        self._filters = set(filters)
        self.sorters = [*sorters]  # This can be public, because changes after instantiation will not affect the data

        self._import_parsers = (PyImportParser,)
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
            result = {}
            changes_made = False

            for parent, children in working_result.items():
                if self.is_valid_file(parent):
                    filtered_children = set()

                    for child in children:
                        if self.is_valid_file(child):
                            filtered_children.add(child)
                        else:
                            changes_made = True

                            for nested_child in self._connections[child]:
                                filtered_children.add(nested_child)

                    result[parent] = filtered_children

                else:
                    changes_made = True  # Entry was filtered out of the result via omission

            working_result = {**result}

        return result

    def generate_scores(self):
        for _path, subdirs, files in walk(self._dir_path):
            for name in files:
                file_path = path.join(_path, name)
                try:
                    self.generate_score(file_path)
                except ExternalFileError:
                    pass
                except NoValidParserError:
                    pass

        return self.scores

    def generate_score(self, file_path):
        file_path = path.abspath(file_path)

        # Preliminary checks
        if file_path[:len(self._dir_path)] != self._dir_path:
            raise ExternalFileError("the file must be located in the specified directory")
        if file_path in self._scores:
            return self._scores[file_path]

        valid_parsers = list(filter(lambda _parser: _parser.can_parse(file_path), self._import_parsers))
        if not valid_parsers:
            raise NoValidParserError("unable to parse provided file")
        parser = valid_parsers[0]

        try:
            with open(file_path) as file:
                contents = file.read()
        except FileNotFoundError:  # Primarily used to weed out builtins
            raise ExternalFileError("the file must be located in the specified directory")

        dependencies_paths = parser.get_dependencies_paths(contents, path.dirname(file_path))

        score = 0
        self._connections[file_path] = set()

        for dependency_path in dependencies_paths:
            do_increment_score = self.is_valid_file(dependency_path)  # Filtered files do not increment score

            try:
                dependency_score = self.generate_score(dependency_path)
                score = max(score, dependency_score+do_increment_score)

                self._connections[file_path].add(dependency_path)
            except ExternalFileError:
                pass
            except NoValidParserError:
                pass

        self._scores[file_path] = score
        return score

    def is_valid_file(self, file_path):
        return all(func(file_path) for func in self._filters)

    def plot_digraph(self, node_size=12500, alpha=0.35):
        """
        Basic grapher to display generated scores/connections. Not guaranteed to produce aesthetic graphs when
        provided with more complex dependency networks
        """

        connections = {}

        # Prettify data labels
        for parent, children in self.connections.items():
            abbreviated_children = set()

            for child in children:
                abbreviated_children.add(self.get_label(child))

            connections[self.get_label(parent)] = abbreviated_children

        graph = DiGraph(connections).reverse()
        draw(graph, with_labels=True, node_size=node_size, alpha=alpha, arrows=True)
        pyplot.show()

    def get_label(self, file_path):
        """
        Provides a concrete implementation for prettifying a file path into a label
        """

        result = file_path.replace(self._dir_path+"\\", "")
        result = result.replace("\\", " ▼\n")

        score = self._scores[file_path]
        max_score = max(*self._scores.values())
        result += "\n\n" + f"({'★' * score}{'☆' * (max_score - score)})"

        return result
