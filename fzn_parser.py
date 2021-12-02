from lark import Lark, Transformer, Token, Tree

from constraints import get_constraint
from node import Node
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
            mynode = Node(item)
            print(mynode)
