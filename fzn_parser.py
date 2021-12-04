import os

from lark import Lark, Transformer, Token, Tree

from node import Node


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
    directories = (
        "/Users/dan/Dropbox/SBU/fall_2021/computing_with_logic/project/cse505parser",
        "/Users/dan/Dropbox/SBU/fall_2021/computing_with_logic/project/cse505parser/quantum_tutorial",
    )
    broken_files = []
    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith(".fzn"):
                # if filename == "set_partition.fzn":
                try:
                    f = f"{directory}/{filename}"
                    flatzinc = open(f, "r")
                    # print()
                    tree = ProcessFlatZinc().transform(
                        Lark.open("grammar.lark").parse(flatzinc.read())
                    )
                    print(f"\n\n{'-'*110}\n{filename}\n{'-'*110}\n")
                    for item in tree.children:
                        if item == None:
                            continue

                        else:
                            mynode = Node(item)
                            print(mynode)
                except Exception as e:
                    broken_files.append(filename)
    print(f"\n\nBroken Files:")
    [print(f) for f in broken_files]
