int: n; % number of objects
array[1..n,1..n] of bool: a; % coefficient matrix
array[1..n] of int: w; % weight vector

array[1..n] of var bool: x; % object decision variables

constraint forall(i in 1..n)(sum(j in 1..n)(a[i,j] * x[j]) <= 1);
solve maximize sum(i in 1..n)(w[i] * x[i]);
