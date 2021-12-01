from lark import Lark, Transformer, Token, Tree

from constraints import get_constraint
from vars import VarDeclNode, ArrayNode


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
    if tree.children[0].data.value == "identifier":
        return tree.children[0].children[0].value


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


class Node:
    def __init__(self, tree):
        self.identifier = self._get_identifier(tree)
        self.expressions = self._get_data(tree)
        self.annotations = self._get_annotations(tree)

    def _get_identifier(self, t: Tree):
        return t.data

    def _get_data(self, t: Tree):
        expressions = []

        y = [child for child in t.children if child.data.type == "expr"]
        return y

    def _get_annotations(self, t: Tree):
        x = [child for child in t.children if child.data.type == "annotations"]
        return x


def get_expression(tre: Tree):
    expr = [c.children[0] for c in tre.children if c.data.value == "expr"]
    ex = []
    for e in expr:
        if isinstance(e, Tree):
            if e.data.value == "var_par_identifier":
                ex.append(e.children[0].value)
            else:
                ex.append(e.children[0])
    return ex


class TargetNode:
    def __init__(self, t: Tree):
        self.var_type = self._get_var_type(t)
        self.var_name = self._get_var_name(t)
        self.annotations = self._get_annotations(t)

    def _get_var_type(self, tree: Tree):
        return tree.data.value

    def _get_var_name(self, tree: Tree):
        var = [child for child in tree.children if child.data == "var_par_identifier"]
        return [c.value for c in var[0].children]

    def _get_annotations(self, tree: Tree):
        return [child for child in tree.children if child.data == "annotations"]


class ParDeclItem:
    name = "par_decl_item"

    def __init__(self, tree: Tree):
        self.node_type = tree.data.value
        self.variable = (
            [x for x in item.children if x.data.value == "var_par_identifier"][0]
            .children[0]
            .value
        )
        self.predicate_type = (
            [x for x in item.children if x.data.value == "par_expr"][0]
            .children[0]
            .data.value
        )
        self.values = (
            [x for x in item.children if x.data.value == "par_expr"][0]
            .children[0]
            .children
        )
        self.expressions = [
            (x.data.value, [y for y in x.children]) for x in item.children
        ]
        self.definitions = [x[0] for x in self.expressions]
        # self.values = [x[1] for x in self.expressions]


if __name__ in "__main__":
    # flatzinc = open("vertex_cover.fzn", "r")
    flatzinc = open("qk.fzn", "r")
    tree = ProcessFlatZinc().transform(Lark.open("grammar.lark").parse(flatzinc.read()))
    obj_func = []
    introduced_nodes = []
    constraints = []
    array_nodes = []
    for item in tree.children:
        if item == None:
            continue
        else:
            if item.data.value == "var_decl_item":
                if item.children[0].data == "array_var_type":
                    an = ArrayNode(item)
                    array_nodes.append(an)

                else:
                    n = VarDeclNode(item)
                    if n.is_introduced:
                        introduced_nodes.append(n)
                    else:
                        obj_func.append(n)

            elif item.data.value == "constraint_item":
                cn = get_constraint(item)
                print(cn.predicate)
                constraints.append(cn)

            elif item.data.value == "par_decl_item":
                pdi = ParDeclItem(item)
                array_nodes.append(pdi)

            else:
                if item.data.value == "solve_item":
                    tn = TargetNode(item)

    print("\n\nObjective Input Nodes")
    print(f"{'-'*100}")
    for of in obj_func:
        print(of.var_name, of.var_values)
    print(f"{'-'*100}\n\n")

    print("Introduced Nodes")
    print(f"{'-'*100}")
    for intro_nodes in introduced_nodes:
        print(intro_nodes.var_name, intro_nodes.var_values)

    print(f"{'-'*100}\n\n")
    print("Constraints Nodes")
    print(f"{'-'*100}")
    for c in constraints:
        print(c.predicate, c.arguments)

    print(f"{'-'*100}\n\n")

    print("Array Nodes")
    print(f"{'-'*100}")
    for a in array_nodes:
        if hasattr(a, "name"):
            print(a.node_type, a.variable, a.values)
        else:
            print(a.var_type, a.var_values)
    print(f"{'-'*100}\n\n")

    print("Target Nodes")
    print(f"{'-'*100}")

    print(f"Target:\t{tn.var_name}")
    print(f"{'-'*100}\n")
