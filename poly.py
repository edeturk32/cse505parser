class Term:
    def __init__(self, coefficient=1, variables=[]):
        self.coefficient = coefficient
        self.variables = variables

    @staticmethod
    def mul(term1, term2):
        product = Term()
        product.coefficient = term1.coefficient * term2.coefficient
        product.variables = term1.variables + term2.variables
        return product

    def __str__(self):
        return "*".join([str(var) for var in ([self.coefficient] + self.variables)])

class Poly:
    def __init__(self, terms=[]):
        self.terms = terms

    def __str__(self):
        return " + ".join([str(term) for term in self.terms])

    @staticmethod
    def distribute(term, poly):
        return Poly(
            terms=([term_mul(term, term2) for term2 in poly.terms])
        )

    @staticmethod
    def add(poly1, poly2):
        return Poly(
            terms=(sop1.terms + sopt2.terms)
        )

    @staticmethod
    def mul(poly1, poly2):
        return Poly(
            terms=([term_mul(term1, term2) for term1 in poly1.terms for term2 in poly2.terms])
        )
