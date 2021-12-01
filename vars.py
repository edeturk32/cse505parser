from lark import Tree


class VarDeclNode:
    def __init__(self, tree: Tree):
        self.node_class = self._node_class(tree)

        self.data_type, self.data_value = self._get_data(tree)
        self.name_type, self.var_name = self._get_name(tree)
        self.var_type, self.var_values = self._get_var_info(tree)
        self.annotations = self._get_annotations(tree)
        self.is_introduced = self._is_introduced()
        self.children = tree.children

    def _node_class(self, tree):
        return tree.data.value

    def _get_data(self, tree: Tree):
        return tree.data.type, tree.data.value

    def _get_var_info(self, tree: Tree):
        return tree.children[0].data.value, tree.children[0].children

    def _get_name(self, tree: Tree):
        return tree.children[1].data.value, tree.children[1].children[0].value

    def _get_annotations(self, tree: Tree):
        if tree.children[2].children == [None]:
            return None
        else:
            return tree.children[2].children

    def _is_introduced(self):
        if isinstance(self.annotations, list):
            if len(self.annotations[0].children) == 1:
                if (
                    self.annotations[0].children[0].children[0].value
                    == "var_is_introduced"
                ):
                    return True
        return False


class ArrayNode(VarDeclNode):
    def __init__(self, t: Tree):
        self.data_type, self.data_value = self._get_data(t)
        self.name_type, self.var_name = self._get_name(t)
        self.var_type, _ = self._get_var_info(t)
        self.var_values = self._get_arguments(t)
        self.annotations = self._get_annotations(t)

    def _get_arguments(self, t: Tree):
        _args = []
        for x in t.children:
            if x.data.value == "array_literal":
                for y in x.children:
                    if y.data.value == "var_par_identifier":
                        _args.append(y.children[0].value)
        return _args
