from lark import Lark, Transformer, Token, Tree
from parse.node import Node
from parse.poly import Poly, Term

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

    def bool(self, children):
        token = Token("placeholder", "basic_var_type")
        tree = Tree(token, [[0, 1]])
        return tree


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
        decision_vars[node.var_par_identifier] = tuple(node.basic_var_type[0])
        subexprs[node.var_par_identifier] = Poly(
            terms=[Term(variables=[node.var_par_identifier])]
        )

def process_subexpr_constraint(node):
    if node.identifier == "bool2int":
        [bool_var, int_var] = node.expr
        assert int_var == node.annotations[1]
        # Now we'll treat the int variable as the decision variable
        decision_vars.pop(bool_var)
        decision_vars[int_var] = (0, 1)
        subexprs[bool_var] = Poly(terms=[Term(variables=[int_var])])
        subexprs[int_var] = Poly(terms=[Term(variables=[int_var])])
    elif node.identifier == "int_times":
        [var1, var2, product] = node.expr
        assert product == node.annotations[1]
        decision_vars.pop(product)
        subexprs[product] = Poly(terms=[Term.mul(Term(variables=[var1]), Term(variables=[var2]))])
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
        inequality_constraints.append((*poly.linear(), constant))
    elif node.identifier == "int_lin_eq":
        [coefficients, variables, constant] = node.expr
        coefficients = parameters[coefficients]
        poly = Poly()
        for i in range(len(variables)):
            poly = Poly.add(poly, Poly(terms=[Term(
                coefficient=coefficients[i],
                variables=[variables[i]]
            )]))
        equality_constraints.append((*poly.linear(), constant))
    elif node.identifier == "array_bool_or":
        variables = node.expr[:-1]
        value = node.expr[-1]
        if value == True:
            inequality_constraints.append((
                [-1] * len(variables),
                variables,
                -1
            ))
        else:
            equality_constraints.append(
                [1] * len(variables),
                variables,
                0
            )


visited = set()
def sub_postorder(variable):
    visited.add(variable)
    old_subexpr = subexprs[variable]
    new_subexpr = old_subexpr
    for term in old_subexpr.terms:
        for var in term.variables:
            if var != subexprs[var].unit():
                if not(var in visited):
                    sub_postorder(var)
                new_subexpr = Poly.substitute(new_subexpr, var, subexprs[var])
    subexprs[variable] = new_subexpr
    return subexprs[variable]

def substitute():
    global objective
    global inequality_constraints
    global equality_constraints
    var, opt = objective
    objective = Poly.substitute(Poly(terms=[Term(variables=[var])]), var, sub_postorder(var))
    if opt == "maximize":
        objective = Poly(terms=[Term(coefficient=(-term.coefficient), variables=term.variables) for term in objective.terms])
    new_inequality_constraints = []
    for coefficients, variables, constant in inequality_constraints:
        new_inequality_constraints.append((
            coefficients,
            [sub_postorder(var).unit() for var in variables],
            constant
        ))
    inequality_constraints = new_inequality_constraints
    new_equality_constraints = []
    for coefficients, variables, constant in equality_constraints:
        new_equality_constraints.append((
            coefficients,
            [sub_postorder(var).unit() for var in variables],
            constant
        ))
    equality_constraints = new_equality_constraints

def parse_flatzinc(flatzinc):
    global objective
    tree = ProcessFlatZinc().transform(
        Lark.open("parse/grammar.lark").parse(flatzinc.read())
    )
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
                #print(item_node)
                process_par(item_node)
            elif item_node.item_type == "var_decl_item":
                #print(item_node)
                process_decl(item_node)
            elif item_node.item_type == "constraint_item" and \
                    item_node.identifier == "bool2int":
                #print(item_node)
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
                    #print(item_node)
                    process_subexpr_constraint(item_node)
                else:
                    #print(item_node)
                    process_constraint(item_node)
            elif item_node.item_type == "minimize":
                objective = (item_node.var_par_identifier, "minimize")
            elif item_node.item_type == "maximize":
                objective = (item_node.var_par_identifier, "maximize")
    substitute()
    #print("\n\nDecision Variables")
    #print(f"{'-'*100}")
    #for dv, vals in decision_vars.items():
    #    print(dv, vals)

    #print(f"{'-'*100}\n\n")
    #print("Inequality constraints")
    #print(f"{'-'*100}")
    #for coefficients, variables, constant in inequality_constraints:
    #    print(coefficients, variables, "<=", constant)

    #print(f"{'-'*100}\n\n")
    #print("Equality constraints")
    #print(f"{'-'*100}")
    #for coefficients, variables, constant in equality_constraints:
    #    print(coefficients, variables, "=", constant)

    #print(f"{'-'*100}\n\n")
    #print("Objective")
    #print(f"{'-'*100}")
    #print("minimize", objective)

    A_le = []
    b_le = []
    for coefficients, variables, constant in inequality_constraints:
        row = []
        for decision_var in decision_vars:
            if decision_var in variables:
                i = variables.index(decision_var)
                row.append(coefficients[i])
            else:
                row.append(0)
        A_le.append(row)
        b_le.append([constant])

    A_eq = []
    b_eq = []
    for coefficients, variables, constant in equality_constraints:
        row = []
        for decision_var in decision_vars:
            if decision_var in variables:
                i = variables.index(decision_var)
                row.append(coefficients[i])
            else:
                row.append(0)
        A_eq.append(row)
        b_eq.append([constant])

    return (
        list(decision_vars.items()),
        A_le,
        b_le,
        A_eq,
        b_eq,
        {tuple(term.variables): term.coefficient for term in objective.terms}
    )
