int: N; % number of vertices
array[1..N,1..N] of bool: e; % adjacency matrix, assumed to be symmetric

array[1..N] of var bool: v;
constraint forall(i in 1..N, j in 1..N where e[i,j])(v[i] \/ v[j]);

solve minimize sum(v);
