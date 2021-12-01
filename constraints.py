from abc import ABC

from lark import Tree


class ConstraintNode(ABC):
    def __init__(self, tree: Tree):
        self.predicate = self._get_predicate(tree)
        self.expressions = self._get_expressions(tree)
        self.annotations = self._get_annotations(tree)
        self._get_variables()
        self._get_constraints()
        self.values = 0
        self.arguments = []

    def _traverse(self, tree, key, data):
        if tree.data.type == key or tree.data.value == data:
            return key
        else:
            return self._traverse(tree, key, data)

    def _get_predicate(self, tree):
        identifiers = [x for x in tree.children if x.data.value == "identifier"]
        return identifiers[0].children[0].value

    def _get_expressions(self, tree):
        return [z for x in tree.children for z in x.children if x.data.value == "expr"]

    def _get_variables(self):
        variables = ""
        return variables

    def _get_constraints(self):
        self.constraints = []

    def _get_annotations(self, tree):
        return [x for x in tree.children if x.data.value == "annotations"][0]


class IntLinLe(ConstraintNode):
    name = "int_lin_le"

    def __init__(self, tree: Tree):
        super().__init__(tree)
        self._get_constraints()
        self._get_variables()
        self._get_values()
        self.arguments = [self.constraints, self.variables, self.values]

    def _get_values(self):
        self.values = [x for x in self.expressions if not isinstance(x, Tree)][0]

    def _get_constraints(self):
        self.constraints = [x.value for x in self.expressions[0].children]

    def _get_variables(self):
        self.variables = [
            child.children[0].value for child in self.expressions[1].children
        ]


class Bool2Int(ConstraintNode):
    name = "bool2int"

    def __init__(self, tree: Tree):
        super().__init__(tree)
        self.arguments = [self.variables]

    def _get_variables(self):
        self.variables = [y.value for x in self.expressions for y in x.children]


class IntLinEq(ConstraintNode):
    name = "int_lin_eq"

    def __init__(self, tree: Tree):
        super().__init__(tree)
        self._get_constraints()
        self._get_variables()
        self._get_values()
        self.arguments = [self.constraints, self.variables, self.values]

    def _get_constraints(self):
        self.constraints = [x for x in self.expressions[0].children]

    def _get_variables(self):
        self.variables = [
            y.value for x in self.expressions[1].children for y in x.children
        ]

    def _get_values(self):
        self.values = self.expressions[2]


class IntTimes(ConstraintNode):
    name = "int_times"

    def __init__(self, tree: Tree):
        super().__init__(tree)
        self._get_variables()
        self.arguments = [self.variables]

    def _get_variables(self):
        self.variables = [y.value for x in self.expressions for y in x.children]


def get_constraint(tree):
    for sub in ConstraintNode.__subclasses__():
        if sub.name == sub._get_predicate(sub, tree):
            return sub(tree)
