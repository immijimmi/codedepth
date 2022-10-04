from networkx import DiGraph, draw_shell as draw
from graphviz import Digraph
from matplotlib import pyplot

from os import path, walk, sep
from sys import setrecursionlimit
from string import ascii_uppercase
from typing import Iterable, Callable, Dict, Set, Tuple, FrozenSet, Type, Optional
from contextlib import contextmanager
from warnings import warn

from .parsers import *
from .colourpickers import *
from .constants import Errors
from .config import Config


@contextmanager
def set_value(target_set, value):
    if value in target_set:
        raise ValueError("value already exists in set")

    target_set.add(value)
    try:
        yield
    finally:
        target_set.remove(value)


class Scorer:
    def __init__(
            self, dir_path: str, config=Config,
            custom_labeller: Optional[Callable[["Scorer", str], Optional[str]]] = None,
            custom_parsers: Iterable[Type[Parser]] = (),
            custom_filters: Iterable[Callable[[str], bool]] = ()
    ):
        self._config = config

        self._dir_path = path.abspath(dir_path)
        # Filtered files do not increment the score of any dependency trees they are in, and are excluded from output
        self._filters = set(custom_filters)
        self._parsers = {PyParser, LuaParser, JsParser}
        self._custom_labeller = custom_labeller or (lambda scorer, file_path: None)

        for parser_cls in custom_parsers:
            self._parsers.add(parser_cls)

        if self._config.USE_DEFAULT_FILTERS:
            for parser_cls in self._parsers:
                for func in parser_cls.FILTERS:
                    self._filters.add(func)

        self._colour_picker = self._config.COLOUR_PICKER_CLS(self)

        # Layer score indicates how many layers of imports a file relies on
        self._layer_scores = {}
        # Abstraction score indicates how many layers away from the nearest top-level file a file is
        self._abstraction_scores = {}

        self._imports = {}
        self._exports = {}

        self._parse_stack = set()

        setrecursionlimit(10000)

    @property
    def config(self):
        return self._config

    @property
    def dir_path(self) -> str:
        return self._dir_path

    @property
    def parsers(self) -> FrozenSet[Type[Parser]]:
        return frozenset(self._parsers)

    @property
    def filters(self) -> FrozenSet[Callable[[str], bool]]:
        return frozenset(self._filters)

    @property
    def layer_scores(self) -> Dict[str, int]:
        """
        Returns data with filtered files removed
        """

        result = {}

        for key, value in self._layer_scores.items():
            if all(func(key) for func in self._filters):
                result.update({key: value})

        return result

    @property
    def abstraction_scores(self) -> Dict[str, int]:
        """
        Returns data with filtered files removed.
        Unlike with layer scores, abstraction scores cannot be calculated with minimal overhead when already calculating
        connections in parse(). Therefore, it is calculated JIT in this property
        """

        if len(self._abstraction_scores) < len(self._layer_scores):
            self._generate_abstraction_scores()

        result = {}

        for key, value in self._abstraction_scores.items():
            if all(func(key) for func in self._filters):
                result.update({key: value})

        return result

    @property
    def imports(self) -> Dict[str, Set[str]]:
        """
        Returns data with filtered files removed
        """

        return self._filtered_connections(self._imports)

    @property
    def exports(self) -> Dict[str, Set[str]]:
        """
        Returns data with filtered files removed
        """

        return self._filtered_connections(self._exports)

    def parse_all(self) -> Dict[str, int]:
        for file_location_path, subdirs, files in walk(self._dir_path):
            for name in files:
                file_path = path.join(file_location_path, name)
                try:
                    self.parse(file_path)
                except Errors.ExternalFileError:
                    pass
                except Errors.NoValidParserError:
                    pass

        return self.layer_scores

    def parse(self, file_path: str) -> int:
        file_path = path.abspath(file_path)

        # Preliminary checks to filter external files out and see if this file's score is already calculated
        if file_path[:len(self._dir_path)] != self._dir_path:
            raise Errors.ExternalFileError("the file must be located in the specified directory")
        if file_path in self._layer_scores:
            return self._layer_scores[file_path]

        # Looking for a parser that can parse this file
        valid_parsers = list(filter(lambda parser_to_check: parser_to_check.can_parse(file_path), self._parsers))
        if not valid_parsers:
            raise Errors.NoValidParserError("unable to parse provided file")
        parser_cls = valid_parsers[0]

        # Reading the file's contents
        try:
            with open(file_path, encoding="utf-8") as file:
                contents = file.read()
        except FileNotFoundError:  # Primarily used to weed out builtins
            raise Errors.ExternalFileError("the file must be located in the specified directory")

        # This indicates whether the file is already being handled further up the stack
        if file_path in self._parse_stack:
            self._layer_scores[file_path] = -1  # Temporary, to indicate that a circular dependency exists
            return 0

        with set_value(self._parse_stack, file_path):
            import_targets = tuple(parser_cls.parse(contents, path.dirname(file_path), self._dir_path))

            # Setup for storing the results of parsing the file
            layer_score = 0
            if file_path not in self._imports:
                self._imports[file_path] = set()
            if file_path not in self._exports:
                self._exports[file_path] = set()

            # Parsing the file's imports to get their scores
            for import_target in import_targets:
                do_increment_layer = self.is_valid_file(import_target)  # Filtered files do not increase layer

                try:
                    dependency_layer = self.parse(import_target)
                    layer_score = max(layer_score, dependency_layer+do_increment_layer)

                    # If self.parse() did not raise exception, import_target is a valid file to add to connections dicts
                    self._imports[file_path].add(import_target)
                    if import_target not in self._exports:
                        self._exports[import_target] = set()
                    self._exports[import_target].add(file_path)
                except Errors.ExternalFileError:
                    pass
                except Errors.NoValidParserError:
                    pass

        # Circular dependencies from further down the stack are handled here
        if self._layer_scores.get(file_path, None) == -1:
            warn(f"a circular dependency was detected in the following file: {file_path}")

            # Remove any listed imports for the flagged file, in order to break the dependency chain
            self._imports[file_path] = set()
            for import_target in import_targets:
                if file_path in self._exports[import_target]:
                    self._exports[import_target].remove(file_path)

            self._layer_scores[file_path] = 0
            return 0

        else:
            self._layer_scores[file_path] = layer_score
            return layer_score

    def is_valid_file(self, file_path: str) -> bool:
        return all(func(file_path) for func in self._filters)

    def plot_circular(self, node_size: int = 12500, alpha: float = 0.35) -> None:
        """
        Plots a circular graph of dependencies using Matplotlib
        (requires matplotlib package)
        """

        warn(
            "this method is no longer supported and will be removed in a future update. "
            "Please use plot_ranked() instead",
            DeprecationWarning
        )

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

    def plot_ranked(self, reversed_score_positioning: bool = True) -> None:
        """
        Plots a ranked dependency graph using Graphviz
        (requires graphviz package, and also for Graphviz to be installed)
        """

        def get_node_id(integer: int) -> str:
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
        scores_working = self.abstraction_scores if reversed_score_positioning else self.layer_scores

        graph = Digraph()
        subgraphs = {}
        node_ids = {}

        for parent_index, parent in enumerate(connections_working):
            node_score = scores_working[parent]
            if node_score not in subgraphs:
                subgraphs[node_score] = Digraph()
                subgraphs[node_score].attr(rank="same")
            subgraph = subgraphs[node_score]

            parent_node_id = get_node_id(parent_index + 1)
            node_ids[parent] = parent_node_id

            node_colour, node_border_colour = self._colour_picker.get(parent)
            subgraph.node(
                parent_node_id, self.get_label(parent),
                color=node_border_colour, style="filled", fillcolor=node_colour, **self._config.RANKED_STYLES["node"]
            )

        for parent_index, parent in enumerate(connections_working):
            parent_node_id = get_node_id(parent_index+1)

            children = connections_working[parent]
            for child in children:
                child_node_id = node_ids[child]

                edge_colour = self._colour_picker.get(child)[1]
                graph.edge(child_node_id, parent_node_id, color=edge_colour, **self._config.RANKED_STYLES["edge"])

        for subgraph in subgraphs.values():
            graph.subgraph(subgraph)

        graph.view()

    def get_label(self, file_path: str, scorebar_chars: Tuple[str, str] = ("■", "□"), scorebar_length: int = 10) -> str:
        """
        Provides a concrete implementation for prettifying a file path into a label
        """

        label_delimiter = "▼\n"
        if (result := self._custom_labeller(self, file_path)) is None:
            result = file_path.replace(self._dir_path + sep, "")
            result = result.replace(sep, label_delimiter)

        if scorebar_length > 0:  # 0 or less will not generate a scorebar at all
            file_layer = self._layer_scores[file_path]
            max_layer = max(self.layer_scores.values())
            scorebar = ""
            for score_index in range(max_layer):
                if score_index % scorebar_length == 0:
                    scorebar += "\n"

                scorebar += (scorebar_chars[not (score_index < file_layer)])

            result += scorebar

        return result

    def _generate_abstraction_scores(self) -> None:
        abstraction_score = 0
        working_exports = self.exports

        while working_exports:
            completed_files = set()

            for parent, children in working_exports.items():
                is_exported = False  # Used to flag if a file is top-level or not in this round of checks
                for child in children:
                    if child in working_exports:
                        is_exported = True
                        break

                if not is_exported:
                    completed_files.add(parent)

            for file_path in completed_files:
                del working_exports[file_path]
                self._abstraction_scores[file_path] = abstraction_score

            abstraction_score -= 1

    def _filtered_connections(self, connections: Dict[str, Iterable[str]]) -> Dict[str, Set[str]]:
        result = {}
        working_result = connections

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

                            for nested_child in connections[child]:
                                filtered_children.add(nested_child)

                    result[parent] = filtered_children

                else:
                    changes_made = True  # Entry was filtered out of the result via omission

            working_result = {**result}

        return result
