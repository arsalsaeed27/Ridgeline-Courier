_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

|   instance |   stops |   d_star | algorithm      | solved   | valid_plan   | reason   | goal_test     |   nodes |   runtime_ms |   max_frontier |   cost |   steps |   cost_over_optimal |
|-----------:|--------:|---------:|:---------------|:---------|:-------------|:---------|:--------------|--------:|-------------:|---------------:|-------:|--------:|--------------------:|
|          0 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      10 |       0.0549 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      10 |       0.0661 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |       6 |       0.0531 |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.0536 |              4 |    nan |     nan |           nan       |
|          0 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      20 |       0.1375 |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      14 |       0.0816 |              9 |     10 |       4 |             1       |
|          0 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      10 |       0.061  |              6 |     10 |       4 |             1       |
|          1 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      17 |       0.1042 |             12 |     21 |       5 |             1       |
|          1 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      46 |       0.2566 |             17 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.0369 |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      22 |       0.1197 |              5 |    nan |     nan |           nan       |
|          1 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      41 |       0.2393 |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.1413 |             14 |     21 |       5 |             1       |
|          1 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      46 |       0.2392 |             17 |     21 |       5 |             1       |
|          2 |       3 |        9 | bfs            | True     | True         | solved   | on generation |      88 |       0.3964 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | ucs            | True     | True         | solved   | on pop        |      95 |       0.4604 |             29 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*)        | True     | True         | solved   | on visit      |     177 |       1.6865 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*-1)      | False    |              | cutoff   | on visit      |     341 |       2.7695 |              9 |    nan |     nan |           nan       |
|          2 |       3 |        9 | ids            | True     | True         | solved   | on visit      |     904 |       8.5922 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | greedy(h_zero) | True     | True         | solved   | on pop        |     108 |       0.8601 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | astar(h_zero)  | True     | True         | solved   | on pop        |      95 |       0.8416 |             29 |     27 |       9 |             1       |
|          3 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     152 |       1.0625 |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       1.6023 |             31 |     55 |      15 |             1       |
|          3 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |     245 |       1.1377 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3779 |      27.3135 |             13 |    nan |     nan |           nan       |
|          3 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    9370 |      58.3334 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.8955 |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       1.3049 |             31 |     55 |      15 |             1       |
|          4 |       3 |       19 | bfs            | True     | True         | solved   | on generation |     165 |       0.6593 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | ucs            | True     | True         | solved   | on pop        |     158 |       0.8214 |             22 |     65 |      21 |             1       |
|          4 |       3 |       19 | dls(d*)        | True     | True         | solved   | on visit      |    2914 |      17.6853 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | dls(d*-1)      | False    |              | cutoff   | on visit      |   81913 |     456.075  |             19 |    nan |     nan |           nan       |
|          4 |       3 |       19 | ids            | True     | True         | solved   | on visit      |  203267 |    1420.62   |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | greedy(h_zero) | True     | True         | solved   | on pop        |     170 |       0.802  |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | astar(h_zero)  | True     | True         | solved   | on pop        |     158 |       0.7554 |             22 |     65 |      21 |             1       |
|          5 |       2 |       12 | bfs            | True     | True         | solved   | on generation |      72 |       0.6987 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | ucs            | True     | True         | solved   | on pop        |      65 |       0.3192 |             12 |     34 |      12 |             1       |
|          5 |       2 |       12 | dls(d*)        | True     | True         | solved   | on visit      |     874 |       4.5348 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1242 |       6.3012 |             12 |    nan |     nan |           nan       |
|          5 |       2 |       12 | ids            | True     | True         | solved   | on visit      |    3770 |      20.3551 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |      78 |       0.9168 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |      65 |       0.5076 |             12 |     34 |      12 |             1       |
|          6 |       2 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.0495 |              7 |      7 |       3 |             1       |
|          6 |       2 |        3 | ucs            | True     | True         | solved   | on pop        |       4 |       0.0331 |              6 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       4 |       0.0348 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0269 |              3 |    nan |     nan |           nan       |
|          6 |       2 |        3 | ids            | True     | True         | solved   | on visit      |       9 |       0.0712 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      13 |       0.0722 |             10 |      7 |       3 |             1       |
|          6 |       2 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       4 |       0.0373 |              6 |      7 |       3 |             1       |
|          7 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      26 |       0.1198 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1475 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      27 |       0.1354 |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.1987 |              6 |    nan |     nan |           nan       |
|          7 |       1 |        6 | ids            | True     | True         | solved   | on visit      |     102 |       0.5152 |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.1372 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1514 |             10 |     26 |       6 |             1       |
|          8 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     207 |       1.3971 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     203 |       1.2305 |             20 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62156 |     314.688  |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |  116025 |     591.695  |             21 |    nan |     nan |           nan       |
|          8 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  385935 |    2043.93   |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     214 |       2.6946 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     203 |       1.0003 |             20 |     59 |      21 |             1       |
|          9 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.0574 |              5 |     11 |       3 |             1       |
|          9 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.073  |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.0533 |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0254 |              3 |    nan |     nan |           nan       |
|          9 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.0912 |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.0589 |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.0701 |              6 |     11 |       3 |             1       |
|         10 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      22 |       0.2248 |             13 |     15 |       5 |             1       |
|         10 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.2654 |             18 |     15 |       7 |             1       |
|         10 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      32 |       0.198  |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.3178 |              5 |    nan |     nan |           nan       |
|         10 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      66 |       0.5933 |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      36 |       0.1902 |             15 |     15 |       5 |             1       |
|         10 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.3562 |             18 |     15 |       7 |             1       |
|         11 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      75 |       0.2938 |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      74 |       0.3267 |             14 |     46 |      14 |             1       |
|         11 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |     994 |       4.5364 |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2000 |      11.1125 |             14 |    nan |     nan |           nan       |
|         11 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    6903 |      35.803  |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      77 |       0.3389 |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      74 |       0.3451 |             14 |     46 |      14 |             1       |
|         12 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      23 |       0.111  |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      28 |       0.1361 |             10 |     20 |       6 |             1       |
|         12 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |       7 |       0.0379 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.2011 |              6 |    nan |     nan |           nan       |
|         12 |       1 |        6 | ids            | True     | True         | solved   | on visit      |      82 |       0.4236 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.1273 |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      28 |       0.1396 |             10 |     20 |       6 |             1       |
|         13 |       3 |       20 | bfs            | True     | True         | solved   | on generation |     150 |       1.1328 |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | ucs            | True     | True         | solved   | on pop        |     168 |       0.7739 |             14 |     76 |      20 |             1       |
|         13 |       3 |       20 | dls(d*)        | True     | True         | solved   | on visit      |     192 |       0.805  |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | dls(d*-1)      | False    |              | cutoff   | on visit      |    7062 |      36.5411 |             20 |    nan |     nan |           nan       |
|         13 |       3 |       20 | ids            | True     | True         | solved   | on visit      |   27044 |     139.763  |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | greedy(h_zero) | True     | True         | solved   | on pop        |     165 |       0.8431 |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | astar(h_zero)  | True     | True         | solved   | on pop        |     168 |       1.216  |             14 |     76 |      20 |             1       |
|         14 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      47 |       0.2285 |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      56 |       0.279  |             16 |     25 |       9 |             1       |
|         14 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      75 |       0.3706 |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      91 |       0.4586 |              7 |    nan |     nan |           nan       |
|         14 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     246 |       1.2486 |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      57 |       0.2559 |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      56 |       0.309  |             16 |     25 |       9 |             1       |
|         15 |       3 |       14 | bfs            | True     | True         | solved   | on generation |     128 |       0.4971 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | ucs            | True     | True         | solved   | on pop        |     166 |       0.7772 |             19 |     62 |      18 |             1       |
|         15 |       3 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    6896 |      41.6131 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5429 |      29.1614 |             14 |    nan |     nan |           nan       |
|         15 |       3 |       14 | ids            | True     | True         | solved   | on visit      |   20114 |     107.838  |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |     137 |       0.6244 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |     166 |       0.8053 |             19 |     62 |      18 |             1       |
|         16 |       3 |       12 | bfs            | True     | True         | solved   | on generation |     131 |       0.9435 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | ucs            | True     | True         | solved   | on pop        |     106 |       0.5391 |             26 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*)        | True     | True         | solved   | on visit      |      72 |       0.3943 |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1916 |      11.022  |             12 |    nan |     nan |           nan       |
|         16 |       3 |       12 | ids            | True     | True         | solved   | on visit      |    4385 |      25.3547 |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |     154 |       0.7136 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |     106 |       0.5565 |             26 |     28 |      12 |             1       |
|         17 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      77 |       0.32   |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      76 |       0.3532 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    2543 |      13.9665 |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3690 |      20.9808 |             14 |    nan |     nan |           nan       |
|         17 |       2 |       14 | ids            | True     | True         | solved   | on visit      |   11158 |      65.0112 |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      80 |       0.4018 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      76 |       0.3535 |             12 |     52 |      14 |             1       |
|         18 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      80 |       0.3694 |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      73 |       0.7415 |             12 |     38 |      14 |             1       |
|         18 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    1881 |       9.9221 |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2696 |      14.7358 |             14 |    nan |     nan |           nan       |
|         18 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    8564 |      49.3878 |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      86 |       0.4357 |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      73 |       0.398  |             12 |     38 |      14 |             1       |
|         19 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.0477 |              5 |     11 |       3 |             1       |
|         19 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.068  |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.0546 |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0272 |              3 |    nan |     nan |           nan       |
|         19 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.1028 |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.0609 |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.0818 |              6 |     11 |       3 |             1       |
|         20 |       3 |       15 | bfs            | True     | True         | solved   | on generation |     156 |       0.6086 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | ucs            | True     | True         | solved   | on pop        |     145 |       0.6554 |             24 |     51 |      15 |             1       |
|         20 |       3 |       15 | dls(d*)        | True     | True         | solved   | on visit      |    2618 |      12.227  |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5655 |      42.6419 |             15 |    nan |     nan |           nan       |
|         20 |       3 |       15 | ids            | True     | True         | solved   | on visit      |   18547 |     103.483  |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.7345 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | astar(h_zero)  | True     | True         | solved   | on pop        |     145 |       0.7035 |             24 |     51 |      15 |             1       |
|         21 |       2 |        6 | bfs            | True     | True         | solved   | on generation |      30 |       0.1561 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1832 |             17 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      48 |       0.2455 |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.2149 |              6 |    nan |     nan |           nan       |
|         21 |       2 |        6 | ids            | True     | True         | solved   | on visit      |     123 |       0.6963 |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      40 |       0.1942 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1827 |             17 |     16 |       6 |             1       |
|         22 |       2 |       18 | bfs            | True     | True         | solved   | on generation |      84 |       0.5005 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | ucs            | True     | True         | solved   | on pop        |      82 |       0.4584 |             10 |     70 |      18 |             1       |
|         22 |       2 |       18 | dls(d*)        | True     | True         | solved   | on visit      |   15015 |      84.5861 |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | dls(d*-1)      | False    |              | cutoff   | on visit      |   20543 |     115.648  |             18 |    nan |     nan |           nan       |
|         22 |       2 |       18 | ids            | True     | True         | solved   | on visit      |   65877 |     359.731  |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | greedy(h_zero) | True     | True         | solved   | on pop        |      88 |       0.4168 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | astar(h_zero)  | True     | True         | solved   | on pop        |      82 |       0.4979 |             10 |     70 |      18 |             1       |
|         23 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      19 |       0.101  |             12 |     17 |       5 |             1       |
|         23 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1593 |             14 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      28 |       0.1421 |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.104  |              5 |    nan |     nan |           nan       |
|         23 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      62 |       0.3264 |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.139  |             13 |     17 |       5 |             1       |
|         23 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.171  |             14 |     17 |       5 |             1       |
|         24 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     131 |       0.766  |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       1.3337 |             23 |     42 |      14 |             1       |
|         24 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |    1795 |       9.813  |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3040 |      17.7084 |             13 |    nan |     nan |           nan       |
|         24 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    8542 |      47.9095 |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     147 |       0.7663 |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       0.8004 |             23 |     42 |      14 |             1       |
|         25 |       1 |        2 | bfs            | True     | True         | solved   | on generation |       3 |       0.0443 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | ucs            | True     | True         | solved   | on pop        |       5 |       0.1254 |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*)        | True     | True         | solved   | on visit      |       3 |       0.1062 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*-1)      | False    |              | cutoff   | on visit      |       1 |       0.0271 |              2 |    nan |     nan |           nan       |
|         25 |       1 |        2 | ids            | True     | True         | solved   | on visit      |       4 |       0.0616 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | greedy(h_zero) | True     | True         | solved   | on pop        |       5 |       0.0788 |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | astar(h_zero)  | True     | True         | solved   | on pop        |       5 |       0.0928 |              5 |      8 |       2 |             1       |
|         26 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     134 |       0.606  |             17 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     113 |       0.5704 |             10 |     75 |      21 |             1       |
|         26 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62771 |     323.485  |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |   79474 |     390.162  |             21 |    nan |     nan |           nan       |
|         26 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  299836 |    1528.5    |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     150 |       0.6594 |             18 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     113 |       0.535  |             10 |     75 |      21 |             1       |
|         27 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      12 |       0.0828 |              6 |     14 |       4 |             1       |
|         27 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      20 |       0.1169 |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |      16 |       0.0933 |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.0577 |              4 |    nan |     nan |           nan       |
|         27 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      30 |       0.1773 |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      18 |       0.0931 |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      20 |       0.1184 |             10 |     14 |       4 |             1       |
|         28 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.041  |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |       8 |       0.0491 |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.0331 |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0235 |              3 |    nan |     nan |           nan       |
|         28 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      10 |       0.0687 |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      10 |       0.0519 |              6 |      9 |       3 |             1       |
|         28 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       8 |       0.0486 |              5 |      9 |       3 |             1       |
|         29 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      41 |       0.1889 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      47 |       0.2581 |             18 |     19 |       9 |             1       |
|         29 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      11 |       0.0585 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      87 |       0.4417 |              7 |    nan |     nan |           nan       |
|         29 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     176 |       1.6467 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      54 |       0.4381 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      47 |       0.3974 |             18 |     19 |       9 |             1       |
