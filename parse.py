from lark import Lark, Transformer

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

flatzinc = open('vertex_cover.fzn', 'r')
tree = ProcessFlatZinc().transform(Lark.open('grammar.lark').parse(flatzinc.read()))

def get_identifier(token):
    return token.children[0].value

def process_array(array):
    return [get_identifier(child) for child in array.children]

def process_annotations(annotations):
    if annotations.children[0] == None:
        return []
    # TODO: handle output array case
    return [annotation.children[0].children[0].value for annotation in annotations.children]

def process_var_decl_item(item):
    # TODO: process variable type and stuff after equals sign
    [_, var_par_identifier, annotations] = item.children[:3]
    #print(var_par_identifier.children[0], process_annotations(annotations))
    print(var_par_identifier.children[0], annotations)

def process_literal(literal):
    if literal.data == 'bool_literal':
        return literal
    if literal.data == 'array_literal':
        return process_array(literal)
    return literal

def process_constraint_item(item):
    for child in item.children:
        if child == None:
            continue
        #if child.data == 'identifier':
        #    print('identifier', get_identifier(child))
        if child.data == 'expr':
            #print('expr', process_literal(child.children[0]))
            print('expr', child.children[0])
        #if child.data == 'annotations':
        #    print('annotations', process_annotations(child))

for item in tree.children:
    if item == None:
        continue
    #if item.data == 'var_decl_item':
    #    process_var_decl_item(item)
    if item.data == 'constraint_item':
        process_constraint_item(item)
