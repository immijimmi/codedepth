from ast import walk, parse, Import, ImportFrom
from contextlib import contextmanager
from sys import path as syspath
from os import path as ospath
from importlib import util


@contextmanager
def temp_path_value(dir_path):
    added = False
    if dir_path not in syspath:
        added = True
        syspath.insert(0, dir_path)
    yield

    if added:
        try:
            syspath.remove(dir_path)
        except ValueError:
            pass


class PyImportParser:
    FILTERS = (
        lambda filename: filename[-12:] != r"\__init__.py",
        lambda filename: filename[-13:] != r"\constants.py"
    )

    @staticmethod
    def can_parse(filename):
        return filename[-3:] == ".py" or filename[-4:] == ".pyw"

    @staticmethod
    def get_dependencies_paths(file_contents, working_dir):
        nodes = walk(parse(file_contents))

        for node in nodes:
            if isinstance(node, Import):
                for name_node in node.names:
                    with temp_path_value(working_dir):
                        origin = util.find_spec(name_node.name).origin
                    yield origin

            elif isinstance(node, ImportFrom):
                offset_working_dir = working_dir

                if node.level > 1:
                    for i in range(node.level-1):
                        offset_working_dir = ospath.dirname(offset_working_dir)  # Go up 1 directory
                if node.module:
                    with temp_path_value(offset_working_dir):
                        origin = util.find_spec(node.module).origin
                    yield origin

                else:
                    for name_node in node.names:
                        with temp_path_value(offset_working_dir):
                            origin = util.find_spec(name_node.name).origin
                        yield origin
