class Term:
    def __init__(self):
        self.coefficient = 1
        self.variables = []

class Poly:
    def __init__(self, terms=[]):
        self.terms = terms

def term_mul(term1, term2):
    product = Term()
    product.coefficient = term1.coeficcient * term2.coefficient
    product.variables = term1.variables + term2.variables
    return product

def poly_add(poly1, poly2):
    return Poly(
        terms=(sop1.terms + sopt2.terms)
    )

def poly_mul(poly1, poly2):
    return Poly(
        terms=([term_mul(term1, term2) for term1 in poly1.terms for term2 in poly2.terms])
    )
