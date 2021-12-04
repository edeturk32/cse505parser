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
                cn = get_constraint(item)
                print(cn.predicate)
                constraints.append(cn)

            elif item.data.value == "par_decl_item":
                pdi = ParDeclItem(item)
                array_nodes.append(pdi)

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
