from networkx import DiGraph, draw_shell as draw
from graphviz import Digraph
from matplotlib import pyplot

from os import path, walk
from sys import setrecursionlimit
from string import ascii_uppercase

from .parsers import PyParser, LuaParser
from .constants import Errors


class DepthScorer:
    def __init__(self, dir_path, filters=(), sorters=(), use_parser_filters=True):
        self._dir_path = path.abspath(dir_path)
        # Filtered files do not increment the score of any dependency trees they are in, and are excluded from output
        self._filters = set(filters)
        self.sorters = [*sorters]  # This can be public, because changes after instantiation will not affect the data

        self._import_parsers = (PyParser, LuaParser)
        if use_parser_filters:
            for parser in self._import_parsers:
                for func in parser.filters:
                    self._filters.add(func)

        self._depths = {}
        self._imports = {}

        setrecursionlimit(10000)

    @property
    def dir_path(self):
        return self._dir_path

    @property
    def depths(self):
        result = {}

        for key, value in self._depths.items():
            if all(func(key) for func in self._filters):
                result.update({key: value})

        return result

    @property
    def depths_items(self):
        result = self.depths.items()

        for func in self.sorters:
            result = sorted(result, key=func)

        return result

    @property
    def imports(self):
        return self._filter_connections(self._imports)

    def parse_all(self):
        for _path, subdirs, files in walk(self._dir_path):
            for name in files:
                file_path = path.join(_path, name)
                try:
                    self.parse(file_path)
                except Errors.ExternalFileError:
                    pass
                except Errors.NoValidParserError:
                    pass

        return self.depths

    def parse(self, file_path):
        file_path = path.abspath(file_path)

        # Preliminary checks
        if file_path[:len(self._dir_path)] != self._dir_path:
            raise Errors.ExternalFileError("the file must be located in the specified directory")
        if file_path in self._depths:
            return self._depths[file_path]

        valid_parsers = list(filter(lambda _parser: _parser.can_parse(file_path), self._import_parsers))
        if not valid_parsers:
            raise Errors.NoValidParserError("unable to parse provided file")
        parser = valid_parsers[0]

        try:
            with open(file_path) as file:
                contents = file.read()
        except FileNotFoundError:  # Primarily used to weed out builtins
            raise Errors.ExternalFileError("the file must be located in the specified directory")

        import_targets = parser.parse(contents, path.dirname(file_path), self._dir_path)

        depth = 0
        self._imports[file_path] = set()

        for import_target in import_targets:
            do_increment_depth = self.is_valid_file(import_target)  # Filtered files do not increase depth

            try:
                dependency_depth = self.parse(import_target)
                depth = max(depth, dependency_depth+do_increment_depth)

                self._imports[file_path].add(import_target)
            except Errors.ExternalFileError:
                pass
            except Errors.NoValidParserError:
                pass

        self._depths[file_path] = depth
        return depth

    def is_valid_file(self, file_path):
        return all(func(file_path) for func in self._filters)

    def plot_circular(self, node_size=12500, alpha=0.35):
        """
        Plots a circular dependency graph using Matplotlib
        (requires matplotlib package)
        """

        connections = {}

        # Prettify data labels
        for parent, children in self.imports.items():
            abbreviated_children = set()

            for child in children:
                abbreviated_children.add(self.get_label(child))

            connections[self.get_label(parent)] = abbreviated_children

        graph = DiGraph(connections).reverse()
        draw(graph, with_labels=True, node_size=node_size, alpha=alpha, arrows=True)
        pyplot.show()

    def plot_ranked(self):
        """
        Plots a ranked dependency graph using Graphviz
        (requires graphviz package, and also for Graphviz to be installed)
        """

        def get_node_id(integer):
            """
            Generates a unique combination of uppercase letters from the provided integer
            """

            if integer < 1:
                raise ValueError("node ID calculation does not work for values less than 1")

            result = ""
            while integer > 0:
                rem = (integer - 1) % 26
                integer = int((integer - rem) / 26)

                result = ascii_uppercase[rem] + result

            return result

        connections_working = self.imports

        graph = Digraph()
        subgraphs = {}
        node_ids = {}

        for parent_index, parent in enumerate(connections_working):
            depth = self._depths[parent]
            if depth not in subgraphs:
                subgraphs[depth] = Digraph()
                subgraphs[depth].attr(rank="same")
            subgraph = subgraphs[depth]

            parent_node_id = get_node_id(parent_index + 1)
            node_ids[parent] = parent_node_id
            subgraph.node(parent_node_id, self.get_label(parent))

        for parent_index, parent in enumerate(connections_working):
            parent_node_id = get_node_id(parent_index+1)

            children = connections_working[parent]
            for child in children:
                child_node_id = node_ids[child]
                graph.edge(child_node_id, parent_node_id)

        for subgraph in subgraphs.values():
            graph.subgraph(subgraph)

        graph.view()

    def get_label(self, file_path, scorebar_chars=("■", "□"), scorebar_length=10):
        """
        Provides a concrete implementation for prettifying a file path into a label
        """

        result = file_path.replace(self._dir_path+"\\", "")
        result = result.replace("\\", " ▼\n")

        if scorebar_length > 0:  # 0 or less will not generate a scorebar at all
            file_depth = self._depths[file_path]
            max_depth = max(self.depths.values())
            scorebar = ""
            for score_index in range(max_depth):
                if score_index % scorebar_length == 0:
                    scorebar += "\n"

                scorebar += (scorebar_chars[not (score_index < file_depth)])

            result += scorebar

        return result

    def _filter_connections(self, connections_dict):
        result = {}
        working_result = connections_dict

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

                            for nested_child in connections_dict[child]:
                                filtered_children.add(nested_child)

                    result[parent] = filtered_children

                else:
                    changes_made = True  # Entry was filtered out of the result via omission

            working_result = {**result}

        return result
