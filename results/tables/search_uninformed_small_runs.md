_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

|   instance |   stops |   d_star | algorithm      | solved   | valid_plan   | reason   | goal_test     |   nodes |   runtime_ms |   max_frontier |   cost |   steps |   cost_over_optimal |
|-----------:|--------:|---------:|:---------------|:---------|:-------------|:---------|:--------------|--------:|-------------:|---------------:|-------:|--------:|--------------------:|
|          0 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      10 |       0.0314 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      10 |       0.0385 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |       6 |       0.0343 |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.0339 |              4 |    nan |     nan |           nan       |
|          0 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      20 |       0.0893 |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      14 |       0.0525 |              9 |     10 |       4 |             1       |
|          0 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      10 |       0.0423 |              6 |     10 |       4 |             1       |
|          1 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      17 |       0.0581 |             12 |     21 |       5 |             1       |
|          1 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      46 |       0.1436 |             17 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.02   |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      22 |       0.0743 |              5 |    nan |     nan |           nan       |
|          1 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      41 |       0.1597 |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.0871 |             14 |     21 |       5 |             1       |
|          1 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      46 |       0.1541 |             17 |     21 |       5 |             1       |
|          2 |       3 |        9 | bfs            | True     | True         | solved   | on generation |      88 |       0.2567 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | ucs            | True     | True         | solved   | on pop        |      95 |       0.2933 |             29 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*)        | True     | True         | solved   | on visit      |     177 |       0.5206 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*-1)      | False    |              | cutoff   | on visit      |     341 |       1.0077 |              9 |    nan |     nan |           nan       |
|          2 |       3 |        9 | ids            | True     | True         | solved   | on visit      |     904 |       2.9264 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | greedy(h_zero) | True     | True         | solved   | on pop        |     108 |       0.3325 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | astar(h_zero)  | True     | True         | solved   | on pop        |      95 |       0.3518 |             29 |     27 |       9 |             1       |
|          3 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     152 |       0.4488 |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       0.5317 |             31 |     55 |      15 |             1       |
|          3 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |     245 |       0.8977 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3779 |      14.7911 |             13 |    nan |     nan |           nan       |
|          3 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    9370 |      32.4629 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.5229 |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       0.652  |             31 |     55 |      15 |             1       |
|          4 |       3 |       19 | bfs            | True     | True         | solved   | on generation |     165 |       0.4848 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | ucs            | True     | True         | solved   | on pop        |     158 |       0.518  |             22 |     65 |      21 |             1       |
|          4 |       3 |       19 | dls(d*)        | True     | True         | solved   | on visit      |    2914 |       9.1111 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | dls(d*-1)      | False    |              | cutoff   | on visit      |   81913 |     273.812  |             19 |    nan |     nan |           nan       |
|          4 |       3 |       19 | ids            | True     | True         | solved   | on visit      |  203267 |     713.526  |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | greedy(h_zero) | True     | True         | solved   | on pop        |     170 |       0.9205 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | astar(h_zero)  | True     | True         | solved   | on pop        |     158 |       0.9445 |             22 |     65 |      21 |             1       |
|          5 |       2 |       12 | bfs            | True     | True         | solved   | on generation |      72 |       0.2048 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | ucs            | True     | True         | solved   | on pop        |      65 |       0.1955 |             12 |     34 |      12 |             1       |
|          5 |       2 |       12 | dls(d*)        | True     | True         | solved   | on visit      |     874 |       2.6956 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1242 |       3.9055 |             12 |    nan |     nan |           nan       |
|          5 |       2 |       12 | ids            | True     | True         | solved   | on visit      |    3770 |      14.6176 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |      78 |       0.2503 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |      65 |       0.2308 |             12 |     34 |      12 |             1       |
|          6 |       2 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.0312 |              7 |      7 |       3 |             1       |
|          6 |       2 |        3 | ucs            | True     | True         | solved   | on pop        |       4 |       0.0211 |              6 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       4 |       0.0217 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0177 |              3 |    nan |     nan |           nan       |
|          6 |       2 |        3 | ids            | True     | True         | solved   | on visit      |       9 |       0.0515 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      13 |       0.0483 |             10 |      7 |       3 |             1       |
|          6 |       2 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       4 |       0.0201 |              6 |      7 |       3 |             1       |
|          7 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      26 |       0.3335 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.3414 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      27 |       0.275  |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.2518 |              6 |    nan |     nan |           nan       |
|          7 |       1 |        6 | ids            | True     | True         | solved   | on visit      |     102 |       0.7011 |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.182  |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1944 |             10 |     26 |       6 |             1       |
|          8 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     207 |       1.0627 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     203 |       1.1486 |             20 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62156 |     302.82   |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |  116025 |     384.544  |             21 |    nan |     nan |           nan       |
|          8 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  385935 |    1304.75   |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     214 |       0.6029 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     203 |       0.6375 |             20 |     59 |      21 |             1       |
|          9 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.0356 |              5 |     11 |       3 |             1       |
|          9 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.0455 |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.0347 |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0164 |              3 |    nan |     nan |           nan       |
|          9 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.0586 |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.0365 |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.0419 |              6 |     11 |       3 |             1       |
|         10 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      22 |       0.0689 |             13 |     15 |       5 |             1       |
|         10 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.104  |             18 |     15 |       7 |             1       |
|         10 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      32 |       0.1036 |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.0666 |              5 |    nan |     nan |           nan       |
|         10 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      66 |       0.2163 |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      36 |       0.1044 |             15 |     15 |       5 |             1       |
|         10 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1097 |             18 |     15 |       7 |             1       |
|         11 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      75 |       0.1812 |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      74 |       0.1998 |             14 |     46 |      14 |             1       |
|         11 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |     994 |       2.7303 |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2000 |       5.8455 |             14 |    nan |     nan |           nan       |
|         11 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    6903 |      19.7835 |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      77 |       0.2144 |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      74 |       0.2176 |             14 |     46 |      14 |             1       |
|         12 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      23 |       0.078  |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      28 |       0.0864 |             10 |     20 |       6 |             1       |
|         12 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |       7 |       0.0252 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.1236 |              6 |    nan |     nan |           nan       |
|         12 |       1 |        6 | ids            | True     | True         | solved   | on visit      |      82 |       0.2614 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.0795 |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      28 |       0.087  |             10 |     20 |       6 |             1       |
|         13 |       3 |       20 | bfs            | True     | True         | solved   | on generation |     150 |       0.365  |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | ucs            | True     | True         | solved   | on pop        |     168 |       0.6192 |             14 |     76 |      20 |             1       |
|         13 |       3 |       20 | dls(d*)        | True     | True         | solved   | on visit      |     192 |       0.5144 |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | dls(d*-1)      | False    |              | cutoff   | on visit      |    7062 |      20.5363 |             20 |    nan |     nan |           nan       |
|         13 |       3 |       20 | ids            | True     | True         | solved   | on visit      |   27044 |      84.8263 |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | greedy(h_zero) | True     | True         | solved   | on pop        |     165 |       0.4808 |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | astar(h_zero)  | True     | True         | solved   | on pop        |     168 |       0.4982 |             14 |     76 |      20 |             1       |
|         14 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      47 |       0.1402 |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      56 |       0.1758 |             16 |     25 |       9 |             1       |
|         14 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      75 |       0.2354 |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      91 |       0.2877 |              7 |    nan |     nan |           nan       |
|         14 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     246 |       0.821  |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      57 |       0.1726 |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      56 |       0.1895 |             16 |     25 |       9 |             1       |
|         15 |       3 |       14 | bfs            | True     | True         | solved   | on generation |     128 |       0.381  |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | ucs            | True     | True         | solved   | on pop        |     166 |       0.5757 |             19 |     62 |      18 |             1       |
|         15 |       3 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    6896 |      25.6238 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5429 |      16.6166 |             14 |    nan |     nan |           nan       |
|         15 |       3 |       14 | ids            | True     | True         | solved   | on visit      |   20114 |      69.1106 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |     137 |       0.4008 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |     166 |       0.5075 |             19 |     62 |      18 |             1       |
|         16 |       3 |       12 | bfs            | True     | True         | solved   | on generation |     131 |       0.3454 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | ucs            | True     | True         | solved   | on pop        |     106 |       0.3146 |             26 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*)        | True     | True         | solved   | on visit      |      72 |       0.231  |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1916 |       6.4262 |             12 |    nan |     nan |           nan       |
|         16 |       3 |       12 | ids            | True     | True         | solved   | on visit      |    4385 |      16.958  |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |     154 |       0.9289 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |     106 |       0.7379 |             26 |     28 |      12 |             1       |
|         17 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      77 |       0.4505 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      76 |       0.4937 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    2543 |      12.6737 |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3690 |      12.1969 |             14 |    nan |     nan |           nan       |
|         17 |       2 |       14 | ids            | True     | True         | solved   | on visit      |   11158 |      39.376  |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      80 |       0.237  |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      76 |       0.2239 |             12 |     52 |      14 |             1       |
|         18 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      80 |       0.3137 |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      73 |       0.211  |             12 |     38 |      14 |             1       |
|         18 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    1881 |       6.1746 |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2696 |       8.9352 |             14 |    nan |     nan |           nan       |
|         18 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    8564 |      30.68   |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      86 |       0.3239 |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      73 |       0.282  |             12 |     38 |      14 |             1       |
|         19 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.0375 |              5 |     11 |       3 |             1       |
|         19 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.0485 |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.0343 |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.017  |              3 |    nan |     nan |           nan       |
|         19 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.059  |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.038  |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.0445 |              6 |     11 |       3 |             1       |
|         20 |       3 |       15 | bfs            | True     | True         | solved   | on generation |     156 |       0.3777 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | ucs            | True     | True         | solved   | on pop        |     145 |       0.4017 |             24 |     51 |      15 |             1       |
|         20 |       3 |       15 | dls(d*)        | True     | True         | solved   | on visit      |    2618 |       8.628  |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5655 |      21.4369 |             15 |    nan |     nan |           nan       |
|         20 |       3 |       15 | ids            | True     | True         | solved   | on visit      |   18547 |      61.1291 |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.5019 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | astar(h_zero)  | True     | True         | solved   | on pop        |     145 |       0.4582 |             24 |     51 |      15 |             1       |
|         21 |       2 |        6 | bfs            | True     | True         | solved   | on generation |      30 |       0.0855 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1033 |             17 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      48 |       0.1428 |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.1268 |              6 |    nan |     nan |           nan       |
|         21 |       2 |        6 | ids            | True     | True         | solved   | on visit      |     123 |       0.4964 |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      40 |       0.2289 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1331 |             17 |     16 |       6 |             1       |
|         22 |       2 |       18 | bfs            | True     | True         | solved   | on generation |      84 |       0.3926 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | ucs            | True     | True         | solved   | on pop        |      82 |       0.2533 |             10 |     70 |      18 |             1       |
|         22 |       2 |       18 | dls(d*)        | True     | True         | solved   | on visit      |   15015 |      58.5576 |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | dls(d*-1)      | False    |              | cutoff   | on visit      |   20543 |      71.7923 |             18 |    nan |     nan |           nan       |
|         22 |       2 |       18 | ids            | True     | True         | solved   | on visit      |   65877 |     238.426  |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | greedy(h_zero) | True     | True         | solved   | on pop        |      88 |       0.2762 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | astar(h_zero)  | True     | True         | solved   | on pop        |      82 |       0.2715 |             10 |     70 |      18 |             1       |
|         23 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      19 |       0.0736 |             12 |     17 |       5 |             1       |
|         23 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1081 |             14 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      28 |       0.0938 |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.0669 |              5 |    nan |     nan |           nan       |
|         23 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      62 |       0.2142 |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.0906 |             13 |     17 |       5 |             1       |
|         23 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1078 |             14 |     17 |       5 |             1       |
|         24 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     131 |       0.3548 |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       0.4674 |             23 |     42 |      14 |             1       |
|         24 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |    1795 |       5.9651 |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3040 |      11.4873 |             13 |    nan |     nan |           nan       |
|         24 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    8542 |      31.4305 |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     147 |       0.4584 |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       0.5373 |             23 |     42 |      14 |             1       |
|         25 |       1 |        2 | bfs            | True     | True         | solved   | on generation |       3 |       0.0177 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | ucs            | True     | True         | solved   | on pop        |       5 |       0.0223 |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*)        | True     | True         | solved   | on visit      |       3 |       0.022  |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*-1)      | False    |              | cutoff   | on visit      |       1 |       0.0074 |              2 |    nan |     nan |           nan       |
|         25 |       1 |        2 | ids            | True     | True         | solved   | on visit      |       4 |       0.0266 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | greedy(h_zero) | True     | True         | solved   | on pop        |       5 |       0.0202 |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | astar(h_zero)  | True     | True         | solved   | on pop        |       5 |       0.0208 |              5 |      8 |       2 |             1       |
|         26 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     134 |       0.328  |             17 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     113 |       0.3085 |             10 |     75 |      21 |             1       |
|         26 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62771 |     204.542  |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |   79474 |     249.355  |             21 |    nan |     nan |           nan       |
|         26 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  299836 |     997.818  |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     150 |       0.5527 |             18 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     113 |       0.5255 |             10 |     75 |      21 |             1       |
|         27 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      12 |       0.0666 |              6 |     14 |       4 |             1       |
|         27 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      20 |       0.1045 |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |      16 |       0.0748 |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.0414 |              4 |    nan |     nan |           nan       |
|         27 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      30 |       0.1416 |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      18 |       0.0736 |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      20 |       0.0938 |             10 |     14 |       4 |             1       |
|         28 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.0317 |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |       8 |       0.0368 |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.0313 |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.019  |              3 |    nan |     nan |           nan       |
|         28 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      10 |       0.0544 |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      10 |       0.0408 |              6 |      9 |       3 |             1       |
|         28 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       8 |       0.0374 |              5 |      9 |       3 |             1       |
|         29 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      41 |       0.1431 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      47 |       0.1832 |             18 |     19 |       9 |             1       |
|         29 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      11 |       0.0431 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      87 |       0.3288 |              7 |    nan |     nan |           nan       |
|         29 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     176 |       0.7017 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      54 |       0.1897 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      47 |       0.1932 |             18 |     19 |       9 |             1       |
