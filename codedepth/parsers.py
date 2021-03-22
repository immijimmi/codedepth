from ast import walk, parse, Import, ImportFrom
from os import path as ospath


class PyImportParser:
    FILTERS = (
        lambda filename: filename[-12:] != r"\__init__.py",
        lambda filename: filename[-13:] != r"\constants.py"
    )

    @staticmethod
    def can_parse(filename):
        return filename[-3:] == ".py" or filename[-4:] == ".pyw"

    @staticmethod
    def parse(file_contents, working_dir):
        nodes = walk(parse(file_contents))

        for node in nodes:
            if isinstance(node, Import):
                for name_node in node.names:
                    target_path = PyImportParser._get_import_target(working_dir, name_node.name)
                    if target_path:
                        yield target_path

            elif isinstance(node, ImportFrom):
                offset_working_dir = working_dir

                if node.level > 1:
                    for i in range(node.level-1):
                        offset_working_dir = ospath.dirname(offset_working_dir)  # Go up 1 directory
                if node.module:
                    target_path = PyImportParser._get_import_target(offset_working_dir, node.module)
                    if target_path:
                        yield target_path

                else:
                    for name_node in node.names:
                        target_path = PyImportParser._get_import_target(offset_working_dir, name_node.name)
                        if target_path:
                            yield target_path

    @staticmethod
    def _get_import_target(working_dir, ast_import_node):
        working_target = working_dir + "\\" + ast_import_node.replace(".", "\\")

        for path_ending in [r"\__init__.py", r"\__init__.pyw", ".py", ".pyw"]:
            result = working_target + path_ending
            if ospath.isfile(result):
                return result
