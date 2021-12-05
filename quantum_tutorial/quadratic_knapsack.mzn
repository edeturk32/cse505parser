int: N; % number of objects
array[1..N,1..N] of int: v; % weight matrix
array[1..N] of int: a; % weight vector
int: b; % budget constraint

array[1..N] of var bool: x; % object decision variables
constraint sum(i in 1..N)(a[i] * x[i]) <= b;

solve maximize sum(i in 1..N-1, j in i..N)(v[i,j] * x[i] * x[j]);
