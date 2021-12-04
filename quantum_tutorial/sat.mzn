% 
% Satisfiability Problem in MiniZinc.
% 
% From GLPK:s example sat.mod
% """
% SAT, Satisfiability Problem
%
% Written in GNU MathProg by Andrew Makhorin <mao@mai2.rcnet.ru>
% """

% 
% This MiniZinc model was created by Hakan Kjellerstrand, hakank@bonetmail.com
% See also my MiniZinc page: http://www.hakank.org/minizinc
%

% number of clauses
int: m;

% number of variables
int: n;

% """
% clauses; each clause C[i], i = 1, ..., m, is disjunction of some
% variables or their negations; in the data section each clause is
% coded as a set of indices of corresponding variables, where negative
% indices mean negation; for example, the clause (x3 or not x7 or x11)
% is coded as the set { 3, -7, 11 }
% """
% set C{1..m};
array[1..m] of set of int: C;


% """
% main variables
% 
% To solve the satisfiability problem means to determine all variables
% x[j] such that conjunction of all clauses C[1] and ... and C[m] takes
% on the value true, i.e. all clauses are satisfied.
%
% Let the clause C[i] be (t or t' or ... or t''), where t, t', ..., t''
% are either variables or their negations. The condition of satisfying
% C[i] can be most naturally written as:
%
%    t + t' + ... + t'' >= 1,                                       (1)
%
% where t, t', t'' have to be replaced by either x[j] or (1 - x[j]).
% The formulation (1) leads to the mip problem with no objective, i.e.
% to a feasibility problem.
%
% Another, more practical way is to write the condition for C[i] as:
%
%    t + t' + ... + t'' + y[i] >= 1,                                (2)
%
% where y[i] is an auxiliary binary variable, and minimize the sum of
% y[i]. If the sum is zero, all y[i] are also zero, and therefore all
% clauses are satisfied. If the sum is minimal but non-zero, its value
% shows the number of clauses which cannot be satisfied.
% """
array[1..n] of var 0..1: x;

% auxiliary variables
array[1..m] of var 0..1: y;


% number of unsatisfied clauses 
var int: unsat = sum(i in 1..m) (y[i]);

solve :: int_search(
    [x[i] | i in 1..n] ++
    [y[i] | i in 1..n] ++
    [unsat],
   first_fail, % "occurrence",
   indomain_min,
   complete
   )
   minimize unsat;
   % satisfy;


constraint
  % the condition (2)
  forall(i in 1..m) (
     % MiniZinc note: this sum works since C[i] is par int, not _var_ int.
     sum(j in C[i]) (
       (if j > 0 then x[j] else (1 - x[-j]) endif) + y[i]
     ) >= 1
  )
  % /\ unsat = 1 % for solve satisfy
;

%output [
%"x: " ++ show(x) ++ "\n"++
%"y: " ++ show(y) ++ "\n"++
%"unsat: " ++ show(unsat) ++ "\n"
%];



