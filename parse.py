from lark import Lark, Transformer, Token, Tree
from poly import Poly, Term

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
        for child in t.children:
            if child.data == "annotations":
                if len(child.children) > 0 and child.children[0] == None:
                    return []
                return [annotation.children for annotation in child.children]

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


class ConstraintNode(Node):
    def __init__(self, tree):
        self.predicate = self._get_predicate(tree)
        if self.predicate == "int_lin_le":
            self.predicate_var = self._get_predicate_var(tree)
        self.arguments = self._get_arguments(tree)
        self.annotations = self._get_annotations(tree)
        self.defines = self._defines()
        self.value = self._get_value(tree)

    def _get_value(self, tree):
        return tree.children[2].children

    def _get_predicate(self, tree):
        for child in tree.children:
            if child.data.value == "identifier":
                return child.children[0].value
        return None

    def _get_arguments(self, tree):
        if self.predicate == "array_bool_or":
            for child in tree.children:
                if (
                    child.data.value == "expr"
                    and child.children[0].data.value == "array_literal"
                ):
                    return self._parse_arguments(child.children[0].children)

        elif self.predicate == "int_lin_eq":
            for child in tree.children:
                if child.data == "expr":
                    return child.children[0].children

        elif self.predicate == "bool2int":
            return [
                x[0].value
                for x in [
                    tree.children[i].children[0].children
                    for i in range(1, len(tree.children))
                    if tree.children[i].data == "expr"
                ]
            ]

        elif self.predicate == "int_lin_le":
            return [
                x.children[0].value
                for x in [
                    child for child in tree.children if child.data.value == "expr"
                ][1]
                .children[0]
                .children
            ]

        if self.predicate == "int_times":
            return get_expression(tree)

    def _get_predicate_var(self, tr: Tree):
        return tr.children[1].children[0].children[0].value

    def _parse_arguments(self, tree_args):
        if all([isinstance(item, Tree) for item in tree_args]):
            return [node.children[0].value for node in tree_args]
        else:
            return tree_args

    def _defines(self):
        if len(self.annotations) > 0 and \
                self.annotations[0][0].children[0].value == "defines_var":
            return self.annotations[0][1].children[0].children[0].children[0].value
        return None

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

decision_vars = {}
undefined_subexprs = set()
subexprs = {}

def process_decl(node):
    if node.is_introduced:
        undefined_subexprs.add(node.var_name)
    else:
        decision_vars[node.var_name] = node.var_values

def process_constraint(node):
    if node.defines == None:
        pass
    else:
        if node.predicate == "bool2int":
            [bool_var, int_var] = node.arguments
            assert int_var == node.defines
            # Now we'll treat the int variable as the decision variable
            undefined_subexprs.remove(int_var)
            decision_vars.pop(bool_var)
            decision_vars[int_var] = [0, 1]
        elif node.predicate == "int_times":
            [factor1, factor2, product] = node.arguments
            factor1 = Term(variables=[factor1])
            factor2 = Term(variables=[factor2])
            assert product == node.defines
            undefined_subexprs.remove(product)
            subexprs[product] = Poly([Term.mul(factor1, factor2)])
        elif node.predicate == "int_lin_eq":
            print(node.arguments)

if __name__ in "__main__":
    # flatzinc = open("vertex_cover.fzn", "r")
    flatzinc = open("vertex_cover.fzn", "r")
    tree = ProcessFlatZinc().transform(Lark.open("grammar.lark").parse(flatzinc.read()))
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
                    process_decl(VarDeclNode(item))

            elif item.data.value == "constraint_item":
                process_constraint(ConstraintNode(item))

            else:
                if item.data.value == "solve_item":
                    tn = TargetNode(item)

    print("\n\nDecision Variables")
    print(f"{'-'*100}")
    for dv, vals in decision_vars.items():
        print(dv, vals)

    print(f"{'-'*100}\n\n")
    print("Undefined Variables")
    print(f"{'-'*100}")
    for iv in undefined_subexprs:
        print(iv)

    print(f"{'-'*100}\n\n")
    print("Subexpressions")
    print(f"{'-'*100}")
    for var, poly in subexprs.items():
        print(var, poly)

    print(f"{'-'*100}\n\n")
    print("Constraints Nodes")
    print(f"{'-'*100}")
    for c in constraints:
        if c.predicate == "int_lin_le":
            print(c.predicate, c.predicate_var, c.arguments)
        else:
            print(c.predicate, c.arguments)
    print(f"{'-'*100}\n\n")

    print("Array Nodes")
    print(f"{'-'*100}")
    for a in array_nodes:
        print(a.var_type, a.var_values)
    print(f"{'-'*100}\n\n")

    print("Target Nodes")
    print(f"{'-'*100}")

    print(f"Target:\t{tn.var_name}")
    print(f"{'-'*100}\n")
