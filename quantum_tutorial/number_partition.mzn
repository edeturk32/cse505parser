int: m; % size of S
array[1..m] of int: S;

array[1..m] of var bool: x; % subset assignment

solve minimize (sum(S) - 2 * sum(i in 1..m)(S[i] * x[i])) * (sum(S) - 2 * sum(i in 1..m)(S[i] * x[i]))
