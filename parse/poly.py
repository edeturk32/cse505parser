def multiset_union(m1, m2):
    keys = set(m1.keys()).union(set(m2.keys()))
    result = {}
    for key in keys:
        result[key] = m1.get(key, 0) + m2.get(key, 0)
    return result

class Term:
    def __init__(self, coefficient=1, variables=[]):
        self.coefficient = coefficient
        self.variables = {var: 1 for var in variables}

    @staticmethod
    def mul(term1, term2):
        product = Term()
        product.coefficient = term1.coefficient * term2.coefficient
        product.variables = multiset_union(term1.variables, term2.variables)
        return product

    @staticmethod
    def substitute(term, variable, poly):
        occurrences = term.variables.get(variable, 0)
        newterm = Term()
        newterm.coefficient = term.coefficient
        newterm.variables = term.variables.copy()
        if variable in newterm.variables:
            newterm.variables.pop(variable)
        if occurrences > 0:
            result = Poly.distribute(newterm, poly)
            occurrences -= 1
            while occurrences > 0:
                result = Poly.mul(result, poly)
                occurrences -= 1
            return result
        else:
            return Poly(terms=[term])

    def __str__(self):
        return str(self.coefficient) + "(" + " * ".join([str(var) + "^" + str(self.variables[var]) for var in self.variables]) + ")"

class Poly:
    def __init__(self, terms=[]):
        self.terms = [term for term in terms if term.coefficient != 0]

    def __str__(self):
        return " + ".join([str(term) for term in self.terms])

    @staticmethod
    def distribute(term, poly):
        return Poly(
            terms=([Term.mul(term, term2) for term2 in poly.terms])
        )

    @staticmethod
    def add(poly1, poly2):
        terms = []
        for new_term in poly1.terms + poly2.terms:
            like_term = False
            for i in range(len(terms)):
                if new_term.variables == terms[i].variables:
                    terms[i] = Term(
                        coefficient=(terms[i].coefficient * new_term.coefficient),
                        variables=new_term.variables
                    )
                like_term = True
                break
            if like_term == False:
                terms.append(new_term)
                    
        return Poly(
            terms=(poly1.terms + poly2.terms)
        )

    @staticmethod
    def mul(poly1, poly2):
        return Poly(
            terms=([Term.mul(term1, term2) for term1 in poly1.terms for term2 in poly2.terms])
        )

    @staticmethod
    def substitute(poly1, variable, poly2):
        res = Poly()
        for term in poly1.terms:
            res = Poly.add(res, Term.substitute(term, variable, poly2))
        return res

    def linear(self):
        coefficients = []
        variables = []
        for term in self.terms:
            coefficients.append(term.coefficient)
            if len(term.variables) == 0:
                variables.append("")
            else:
                variable, multiplicity = next(iter(term.variables.items()))
                if len(term.variables) > 1 or multiplicity > 1:
                    return None
                variables.append(variable)
        return (coefficients, variables)

    def unit(self):
        if len(self.terms) != 1:
            return None
        variable, multiplicity = next(iter(self.terms[0].variables.items()))
        if self.terms[0].coefficient != 1 or multiplicity != 1:
            return None
        return variable
