from lark import Lark, Transformer, Tree


class ProcessFlatZinc(Transformer):
    def basic_expr(self, subexprs):
        return subexprs[0]

    def basic_literal_expr(self, subexprs):
        return subexprs[0]

    def int_literal(self, children):
        return int(children[0].value)

    def false(self, children):
        return False

    def true(self, children):
        return True


def get_identifier(token):
    return token.children[0].value


def process_array(array):
    return [get_identifier(child) for child in array.children]


def process_annotations(annotations):
    if annotations.children[0] == None:
        return []
    # TODO: handle output array case
    return [
        annotation.children[0].children[0].value for annotation in annotations.children
    ]


def process_var_decl_item(item):
    # TODO: process variable type and stuff after equals sign
    [_, var_par_identifier, annotations] = item.children[:3]
    # print(var_par_identifier.children[0], process_annotations(annotations))
    print(var_par_identifier.children[0], annotations)


def process_literal(literal):
    if literal.data == "bool_literal":
        return literal
    if literal.data == "array_literal":
        return process_array(literal)
    return literal


def process_constraint_item(item):
    constraints = {}
    for child in item.children:
        if child == None:
            continue
        # if child.data == 'identifier':
        #    print('identifier', get_identifier(child))
        elif child.data == "expr":
            # print('expr', process_literal(child.children[0]))
            print("expr", child.children[0])
        # if child.data == 'annotations':
        #    print('annotations', process_annotations(child))
        else:
            print(child.data)


class VarDeclNode:
    def __init__(self, tree: Tree):
        self.data_type, self.data_value = self._get_data(tree)
        self.name_type, self.var_name = self._get_name(tree)
        self.var_type, self.var_values = self._get_var_info(tree)
        self.annotations = self._get_annotations(tree)
        self.is_introduced = self._is_introduced()
        self.children = tree.children

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


class ConstraintNode(VarDeclNode):
    def __init__(self, tree):
        self.predicate = self._get_predicate(tree)
        self.arguments = self._get_arguments(tree)
        self.value = self._get_value(tree)

        """
        self.data_type, self.data_value = self._get_data(tree)
        self.name_type, self.var_name = self._get_name(tree)
        self.var_type, self.var_values = self._get_var_info(tree)
        self.annotations = self._get_annotations(tree)
        self.is_introduced = self._is_introduced()
        self.children = tree.children
        assert len(self.children) == 4
        """

    def _get_value(self, tree):
        return tree.children[2].children

    def _get_predicate(self, tree):
        for child in tree.children:
            if child.data.value == "identifier":
                return child.children[0].value
        return None

    def _get_arguments(self, tree):
        for child in tree.children:
            if (
                child.data.value == "expr"
                and child.children[0].data.value == "array_literal"
            ):
                return self._parse_arguments(child.children[0].children)

    def _get_arguments(self, tree):
        x = []
        for child in tree.children:
            if child.data == "expr":
                x = [
                    node.children[0].value
                    for node in child.children
                    if isinstance(node, Tree)
                ]
                return x
        return

    def _parse_arguments(self, tree_args):
        if all([isinstance(item, Tree) for item in tree_args]):
            return [node.children[0].value for node in tree_args]
        else:
            return tree_args


if __name__ in "__main__":
    flatzinc = open("vertex_cover.fzn", "r")
    tree = ProcessFlatZinc().transform(Lark.open("grammar.lark").parse(flatzinc.read()))
    obj_func = []
    introduced_nodes = []
    constraints = []
    for item in tree.children:
        if item == None:
            continue
        else:
            if item.data.value == "var_decl_item":
                n = VarDeclNode(item)

                if n.var_name == "v":
                    print()
                if n.is_introduced:
                    introduced_nodes.append(n)
                else:
                    obj_func.append(n)

            elif item.data.value == "constraint_item":
                cn = ConstraintNode(item)
                if cn.predicate == "bool2int":
                    print()
                constraints.append(ConstraintNode(item))

            else:
                pass

    print(len(obj_func), len(introduced_nodes), len(constraints))
    for of in obj_func:
        print(of.var_name, of.var_values)

    print(f"\n\n{'-'*100}\n\n")
    for intro_nodes in introduced_nodes:
        print(intro_nodes.var_name, intro_nodes.var_values)

    print(f"\n\n{'-'*100}\n\n")
    for c in constraints:
        print(c.predicate, c.arguments)
