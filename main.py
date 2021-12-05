import sys
from parse.parse import parse_flatzinc

if __name__ in "__main__":
    flatzinc = open(sys.argv[1], "r")
    decision_vars, A_le, b_le, A_eq, b_eq, objective = parse_flatzinc(flatzinc)
