from lark import Token, Tree


class Node:
    def __init__(self, tree: Tree):
        if isinstance(tree.data, str):
            self.item_type = tree.data
        else:
            self.item_type = tree.data.value
        if self.item_type == "predicate":
            print()
        self.__dict__.update(self.parse_tree(tree))
        # TODO: Do I need this?
        # self.item_type = None  # basic_par_type, par_type, basic_var_type
        self.prune_class()

    def parse_tree(self, tree):
        parsed_tree = {}
        # things[item_type] = tree.data.value  # Constraint, Parameter, Solver, etc
        for k in tree.children:
            if k:
                things = self.get_things(k.children)
                if isinstance(things, list) and all(
                    [isinstance(i, int) for i in things]
                ):
                    things = [things]

                if isinstance(parsed_tree.get(k.data.value), list):
                    parsed_tree[k.data.value].append(things)

                elif not isinstance(parsed_tree.get(k.data.value, []), list):
                    parsed_tree[k.data.value] = [parsed_tree[k.data.value]]
                    parsed_tree[k.data.value].append(things)

                else:
                    parsed_tree[k.data.value] = things

        return parsed_tree

    def get_things(self, items):
        f = None
        if items == [None] or items == None or items == []:
            f = True

        elif isinstance(items, list):
            f = [self.get_values(i) for i in items]
            if len(f) == 1:
                f = f[0]

        else:
            print(items)

        return f

    def get_values(self, item):
        if isinstance(item, Token):
            return item.value

        elif isinstance(item, Tree):
            return self.get_values(item.children)

        elif isinstance(item, list) and len(item) > 0:
            if len(item) == 1:
                return self.get_values(item[0])

            elif isinstance(item[0], Tree):
                return [self.get_values(i) for i in item]

            else:
                return item

        else:
            return item

    def get_keys(self, item):
        if isinstance(item, Tree):
            return item.data.value

        elif isinstance(item, Token):
            return item.type

    def __repr__(self):
        r = ""
        for key, value in self.__dict__.items():
            r += f"{key}: {value}\t"
        return r

    def __str__(self):
        return self.__repr__()

    def prune_class(self):
        for key, value in self.__dict__.items():
            if isinstance(self.__dict__[key], list) and all(
                [i == None for i in self.__dict__[key]]
            ):
                self.__dict__[key] = True
