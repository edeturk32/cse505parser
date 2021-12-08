int: V; % number of objects
array[1..V,1..V] of bool: E; % adjacency matrix

array[1..V] of var bool: x; % vertex decision variables

solve maximize sum(i,j in 1..V where i < j /\ E[i,j])(x[i] + x[j] - 2 * x[i] * x[j]);
