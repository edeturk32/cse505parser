import os

from lark import Lark, Transformer, Token, Tree
from node import Node
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


decision_vars = {}
subexprs = {}
parameters = {}
inequality_constraints = []
equality_constraints = []
objective = None


def process_par(node):
    if isinstance(node.par_expr, list):
        parameters[node.var_par_identifier] = node.par_expr[0]

def process_decl(node):
    if not('output_array' in node.annotations):
        decision_vars[node.var_par_identifier] = node.basic_var_type
        subexprs[node.var_par_identifier] = Poly(
            terms=[Term(variables=[node.var_par_identifier])]
        )

def process_subexpr_constraint(node):
    if node.identifier == "bool2int":
        [bool_var, int_var] = node.expr
        assert int_var == node.annotations[1]
        # Now we'll treat the int variable as the decision variable
        decision_vars.pop(bool_var)
        decision_vars[int_var] = [0, 1]
        subexprs[bool_var] = Poly(terms=[Term(variables=[int_var])])
        subexprs[int_var] = Poly(terms=[Term(variables=[int_var])])
    elif node.identifier == "int_times":
        [var1, var2, product] = node.expr
        assert product == node.annotations[1]
        decision_vars.pop(product)
        subexprs[product] = Poly.mul(subexprs[var1], subexprs[var2])
    elif node.identifier == "int_lin_eq":
        [coefficients, variables, constant] = node.expr
        defined_var = node.annotations[1]
        index = variables.index(defined_var)
        assert index >= 0
        assert abs(coefficients[index]) == 1
        decision_vars.pop(defined_var)
        terms = [Term(coefficient=constant)]
        for i in range(len(coefficients)):
            if i == index:
                continue
            terms.append(Term(
                coefficient=(-coefficients[i] * coefficients[index]),
                variables=[variables[i]]
            ))
        poly = Poly(terms=terms)
        for var in variables:
            if var == defined_var:
                continue
            poly = poly.substitute(poly, var, subexprs[var])
        subexprs[defined_var] = poly

def process_constraint(node):
    if node.identifier == "int_lin_le":
        [coefficients, variables, constant] = node.expr
        coefficients = parameters[coefficients]
        poly = Poly()
        for i in range(len(variables)):
            poly = Poly.add(poly, Poly(terms=[Term(
                coefficient=coefficients[i],
                variables=[variables[i]]
            )]))
            poly = Poly.substitute(poly, variables[i], subexprs[variables[i]])
        inequality_constraints.append((poly.linear(), constant))
    elif node.identifier == "int_lin_eq":
        [coefficients, variables, constant] = node.expr
        coefficients = parameters[coefficients]
        poly = Poly()
        for i in range(len(variables)):
            poly = Poly.add(poly, Poly(terms=[Term(
                coefficient=coefficients[i],
                variables=[variables[i]]
            )]))
            poly = Poly.substitute(poly, variables[i], subexprs[variables[i]])
        equality_constraints.append((poly.linear(), constant))
    elif node.identifier == "array_bool_or":
        variables = node.expr[:-1]
        value = node.expr[-1]
        if value == True:
            inequality_constraints.append((
                ([-1] * len(variables), [subexprs[var].unit() for var in variables]),
                -1
            ))
        else:
            equality_constraints.append((
                ([1] * len(variables), [subexprs[var].unit() for var in variables]),
                0
            ))

if __name__ in "__main__":
    directories = (
        ".",
        "./quantum_tutorial",
    )
    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith(".fzn"):
                if filename == "set_partitioning.fzn":
                    f = f"{directory}/{filename}"
                    flatzinc = open(f, "r")
                    # print()
                    tree = ProcessFlatZinc().transform(
                        Lark.open("grammar.lark").parse(flatzinc.read())
                    )
                    print(f"\n\n{'-'*110}\n{filename}\n{'-'*110}\n")
                    # First pass for parameters and boolean variables
                    for item in tree.children:
                        if item == None:
                            continue
                        else:
                            item_node = Node(item)
                            if 'annotations' in item_node.__dict__ and \
                                    item_node.annotations == True:
                                item_node.annotations = []
                            if item_node.item_type == "par_decl_item":
                                print(item_node)
                                process_par(item_node)
                            elif item_node.item_type == "var_decl_item":
                                print(item_node)
                                process_decl(item_node)
                            elif item_node.item_type == "constraint_item" and \
                                    item_node.identifier == "bool2int":
                                print(item_node)
                                process_subexpr_constraint(item_node)
                            
                    for item in tree.children:
                        if item == None:
                            continue
                        else:
                            item_node = Node(item)
                            if 'annotations' in item_node.__dict__ and \
                                    item_node.annotations == True:
                                item_node.annotations = []
                            if item_node.item_type == "constraint_item" and \
                                    item_node.identifier != "bool2int":
                                if "defines_var" in item_node.annotations:
                                    print(item_node)
                                    process_subexpr_constraint(item_node)
                                else:
                                    print(item_node)
                                    process_constraint(item_node)
                            elif item_node.item_type == "minimize":
                                objective = subexprs[item_node.var_par_identifier]
                            elif item_node.item_type == "maximize":
                                objective = Poly.mul(
                                    Poly(terms=[Term(coefficient=-1)]),
                                    subexprs[item_node.var_par_identifier]
                                )
                    print("\n\nDecision Variables")
                    print(f"{'-'*100}")
                    for dv, vals in decision_vars.items():
                        print(dv, vals)

                    print(f"{'-'*100}\n\n")
                    print("Inequality constraints")
                    print(f"{'-'*100}")
                    for poly, constant in inequality_constraints:
                        print(poly, "<=", constant)

                    print(f"{'-'*100}\n\n")
                    print("Equality constraints")
                    print(f"{'-'*100}")
                    for poly, constant in equality_constraints:
                        print(poly, "=", constant)

                    print(f"{'-'*100}\n\n")
                    print("Objective")
                    print(f"{'-'*100}")
                    print("minimize", objective)
