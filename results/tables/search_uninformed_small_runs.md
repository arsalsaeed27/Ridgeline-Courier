_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

|   instance |   stops |   d_star | algorithm      | solved   | valid_plan   | reason   | goal_test     |   nodes |   runtime_ms |   max_frontier |   cost |   steps |   cost_over_optimal |
|-----------:|--------:|---------:|:---------------|:---------|:-------------|:---------|:--------------|--------:|-------------:|---------------:|-------:|--------:|--------------------:|
|          0 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      10 |       0.0354 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      10 |       0.0432 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |       6 |       0.037  |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.036  |              4 |    nan |     nan |           nan       |
|          0 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      20 |       0.0938 |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      14 |       0.0561 |              9 |     10 |       4 |             1       |
|          0 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      10 |       0.0438 |              6 |     10 |       4 |             1       |
|          1 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      17 |       0.0689 |             12 |     21 |       5 |             1       |
|          1 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      46 |       0.1638 |             17 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.0245 |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      22 |       0.0837 |              5 |    nan |     nan |           nan       |
|          1 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      41 |       0.164  |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.1012 |             14 |     21 |       5 |             1       |
|          1 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      46 |       0.1837 |             17 |     21 |       5 |             1       |
|          2 |       3 |        9 | bfs            | True     | True         | solved   | on generation |      88 |       0.2675 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | ucs            | True     | True         | solved   | on pop        |      95 |       0.3237 |             29 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*)        | True     | True         | solved   | on visit      |     177 |       0.5761 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*-1)      | False    |              | cutoff   | on visit      |     341 |       1.2024 |              9 |    nan |     nan |           nan       |
|          2 |       3 |        9 | ids            | True     | True         | solved   | on visit      |     904 |       3.0092 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | greedy(h_zero) | True     | True         | solved   | on pop        |     108 |       0.3346 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | astar(h_zero)  | True     | True         | solved   | on pop        |      95 |       0.3397 |             29 |     27 |       9 |             1       |
|          3 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     152 |       0.409  |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       0.4799 |             31 |     55 |      15 |             1       |
|          3 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |     245 |       0.7502 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3779 |      13.6314 |             13 |    nan |     nan |           nan       |
|          3 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    9370 |      31.7291 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.4785 |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       0.5068 |             31 |     55 |      15 |             1       |
|          4 |       3 |       19 | bfs            | True     | True         | solved   | on generation |     165 |       0.4363 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | ucs            | True     | True         | solved   | on pop        |     158 |       0.4852 |             22 |     65 |      21 |             1       |
|          4 |       3 |       19 | dls(d*)        | True     | True         | solved   | on visit      |    2914 |      10.2311 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | dls(d*-1)      | False    |              | cutoff   | on visit      |   81913 |     285.123  |             19 |    nan |     nan |           nan       |
|          4 |       3 |       19 | ids            | True     | True         | solved   | on visit      |  203267 |     702.076  |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | greedy(h_zero) | True     | True         | solved   | on pop        |     170 |       0.5455 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | astar(h_zero)  | True     | True         | solved   | on pop        |     158 |       0.5311 |             22 |     65 |      21 |             1       |
|          5 |       2 |       12 | bfs            | True     | True         | solved   | on generation |      72 |       0.2165 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | ucs            | True     | True         | solved   | on pop        |      65 |       0.2128 |             12 |     34 |      12 |             1       |
|          5 |       2 |       12 | dls(d*)        | True     | True         | solved   | on visit      |     874 |       3.3246 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1242 |       4.3541 |             12 |    nan |     nan |           nan       |
|          5 |       2 |       12 | ids            | True     | True         | solved   | on visit      |    3770 |      14.4212 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |      78 |       0.2606 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |      65 |       0.2376 |             12 |     34 |      12 |             1       |
|          6 |       2 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.0345 |              7 |      7 |       3 |             1       |
|          6 |       2 |        3 | ucs            | True     | True         | solved   | on pop        |       4 |       0.023  |              6 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       4 |       0.0228 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0182 |              3 |    nan |     nan |           nan       |
|          6 |       2 |        3 | ids            | True     | True         | solved   | on visit      |       9 |       0.0526 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      13 |       0.052  |             10 |      7 |       3 |             1       |
|          6 |       2 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       4 |       0.0239 |              6 |      7 |       3 |             1       |
|          7 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      26 |       0.0836 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1079 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      27 |       0.0937 |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.1384 |              6 |    nan |     nan |           nan       |
|          7 |       1 |        6 | ids            | True     | True         | solved   | on visit      |     102 |       0.3651 |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.0919 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1066 |             10 |     26 |       6 |             1       |
|          8 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     207 |       0.6203 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     203 |       0.6599 |             20 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62156 |     250.703  |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |  116025 |     389.345  |             21 |    nan |     nan |           nan       |
|          8 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  385935 |    1288.44   |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     214 |       1.0606 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     203 |       0.8262 |             20 |     59 |      21 |             1       |
|          9 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.0368 |              5 |     11 |       3 |             1       |
|          9 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.0501 |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.037  |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0174 |              3 |    nan |     nan |           nan       |
|          9 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.0707 |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.0403 |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.0494 |              6 |     11 |       3 |             1       |
|         10 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      22 |       0.0896 |             13 |     15 |       5 |             1       |
|         10 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1195 |             18 |     15 |       7 |             1       |
|         10 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      32 |       0.135  |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.0891 |              5 |    nan |     nan |           nan       |
|         10 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      66 |       0.2674 |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      36 |       0.1328 |             15 |     15 |       5 |             1       |
|         10 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1275 |             18 |     15 |       7 |             1       |
|         11 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      75 |       0.2136 |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      74 |       0.341  |             14 |     46 |      14 |             1       |
|         11 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |     994 |       3.1906 |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2000 |       6.8669 |             14 |    nan |     nan |           nan       |
|         11 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    6903 |      22.1231 |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      77 |       0.238  |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      74 |       0.2425 |             14 |     46 |      14 |             1       |
|         12 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      23 |       0.0759 |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      28 |       0.0967 |             10 |     20 |       6 |             1       |
|         12 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |       7 |       0.0252 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.1384 |              6 |    nan |     nan |           nan       |
|         12 |       1 |        6 | ids            | True     | True         | solved   | on visit      |      82 |       0.2944 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.0907 |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      28 |       0.1093 |             10 |     20 |       6 |             1       |
|         13 |       3 |       20 | bfs            | True     | True         | solved   | on generation |     150 |       0.7917 |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | ucs            | True     | True         | solved   | on pop        |     168 |       0.6095 |             14 |     76 |      20 |             1       |
|         13 |       3 |       20 | dls(d*)        | True     | True         | solved   | on visit      |     192 |       0.5638 |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | dls(d*-1)      | False    |              | cutoff   | on visit      |    7062 |      21.5834 |             20 |    nan |     nan |           nan       |
|         13 |       3 |       20 | ids            | True     | True         | solved   | on visit      |   27044 |      88.7833 |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | greedy(h_zero) | True     | True         | solved   | on pop        |     165 |       0.4978 |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | astar(h_zero)  | True     | True         | solved   | on pop        |     168 |       0.8533 |             14 |     76 |      20 |             1       |
|         14 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      47 |       0.1477 |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      56 |       0.2046 |             16 |     25 |       9 |             1       |
|         14 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      75 |       0.2533 |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      91 |       0.3029 |              7 |    nan |     nan |           nan       |
|         14 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     246 |       0.8421 |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      57 |       0.1719 |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      56 |       0.1946 |             16 |     25 |       9 |             1       |
|         15 |       3 |       14 | bfs            | True     | True         | solved   | on generation |     128 |       0.3517 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | ucs            | True     | True         | solved   | on pop        |     166 |       0.5288 |             19 |     62 |      18 |             1       |
|         15 |       3 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    6896 |      22.6673 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5429 |      20.1718 |             14 |    nan |     nan |           nan       |
|         15 |       3 |       14 | ids            | True     | True         | solved   | on visit      |   20114 |      69.2367 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |     137 |       0.4319 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |     166 |       0.5721 |             19 |     62 |      18 |             1       |
|         16 |       3 |       12 | bfs            | True     | True         | solved   | on generation |     131 |       0.3791 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | ucs            | True     | True         | solved   | on pop        |     106 |       0.3829 |             26 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*)        | True     | True         | solved   | on visit      |      72 |       0.4034 |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1916 |       6.6246 |             12 |    nan |     nan |           nan       |
|         16 |       3 |       12 | ids            | True     | True         | solved   | on visit      |    4385 |      15.3529 |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |     154 |       0.4851 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |     106 |       0.784  |             26 |     28 |      12 |             1       |
|         17 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      77 |       0.2117 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      76 |       0.2338 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    2543 |       9.1509 |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3690 |      13.411  |             14 |    nan |     nan |           nan       |
|         17 |       2 |       14 | ids            | True     | True         | solved   | on visit      |   11158 |      38.906  |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      80 |       0.2781 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      76 |       0.2455 |             12 |     52 |      14 |             1       |
|         18 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      80 |       0.238  |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      73 |       0.2681 |             12 |     38 |      14 |             1       |
|         18 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    1881 |       6.616  |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2696 |       9.4848 |             14 |    nan |     nan |           nan       |
|         18 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    8564 |      29.4663 |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      86 |       0.2802 |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      73 |       0.4027 |             12 |     38 |      14 |             1       |
|         19 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.038  |              5 |     11 |       3 |             1       |
|         19 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.0495 |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.0361 |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0172 |              3 |    nan |     nan |           nan       |
|         19 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.0599 |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.0399 |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.0474 |              6 |     11 |       3 |             1       |
|         20 |       3 |       15 | bfs            | True     | True         | solved   | on generation |     156 |       0.4171 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | ucs            | True     | True         | solved   | on pop        |     145 |       0.4498 |             24 |     51 |      15 |             1       |
|         20 |       3 |       15 | dls(d*)        | True     | True         | solved   | on visit      |    2618 |       7.9052 |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5655 |      18.7691 |             15 |    nan |     nan |           nan       |
|         20 |       3 |       15 | ids            | True     | True         | solved   | on visit      |   18547 |      61.3796 |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.4858 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | astar(h_zero)  | True     | True         | solved   | on pop        |     145 |       0.5239 |             24 |     51 |      15 |             1       |
|         21 |       2 |        6 | bfs            | True     | True         | solved   | on generation |      30 |       0.1527 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1435 |             17 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      48 |       0.175  |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.163  |              6 |    nan |     nan |           nan       |
|         21 |       2 |        6 | ids            | True     | True         | solved   | on visit      |     123 |       0.5888 |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      40 |       0.1415 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.2365 |             17 |     16 |       6 |             1       |
|         22 |       2 |       18 | bfs            | True     | True         | solved   | on generation |      84 |       0.2397 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | ucs            | True     | True         | solved   | on pop        |      82 |       0.2561 |             10 |     70 |      18 |             1       |
|         22 |       2 |       18 | dls(d*)        | True     | True         | solved   | on visit      |   15015 |      51.4074 |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | dls(d*-1)      | False    |              | cutoff   | on visit      |   20543 |      71.8953 |             18 |    nan |     nan |           nan       |
|         22 |       2 |       18 | ids            | True     | True         | solved   | on visit      |   65877 |     228.588  |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | greedy(h_zero) | True     | True         | solved   | on pop        |      88 |       0.2841 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | astar(h_zero)  | True     | True         | solved   | on pop        |      82 |       0.2826 |             10 |     70 |      18 |             1       |
|         23 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      19 |       0.0743 |             12 |     17 |       5 |             1       |
|         23 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1153 |             14 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      28 |       0.0996 |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.0722 |              5 |    nan |     nan |           nan       |
|         23 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      62 |       0.227  |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.0985 |             13 |     17 |       5 |             1       |
|         23 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1782 |             14 |     17 |       5 |             1       |
|         24 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     131 |       0.3721 |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       0.5084 |             23 |     42 |      14 |             1       |
|         24 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |    1795 |       6.4036 |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3040 |      10.6391 |             13 |    nan |     nan |           nan       |
|         24 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    8542 |      31.6296 |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     147 |       0.4921 |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       0.5433 |             23 |     42 |      14 |             1       |
|         25 |       1 |        2 | bfs            | True     | True         | solved   | on generation |       3 |       0.0251 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | ucs            | True     | True         | solved   | on pop        |       5 |       0.0298 |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*)        | True     | True         | solved   | on visit      |       3 |       0.018  |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*-1)      | False    |              | cutoff   | on visit      |       1 |       0.0084 |              2 |    nan |     nan |           nan       |
|         25 |       1 |        2 | ids            | True     | True         | solved   | on visit      |       4 |       0.0273 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | greedy(h_zero) | True     | True         | solved   | on pop        |       5 |       0.023  |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | astar(h_zero)  | True     | True         | solved   | on pop        |       5 |       0.0249 |              5 |      8 |       2 |             1       |
|         26 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     134 |       0.3742 |             17 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     113 |       0.3453 |             10 |     75 |      21 |             1       |
|         26 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62771 |     203.106  |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |   79474 |     248.255  |             21 |    nan |     nan |           nan       |
|         26 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  299836 |     977.462  |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     150 |       0.4664 |             18 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     113 |       0.3759 |             10 |     75 |      21 |             1       |
|         27 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      12 |       0.0524 |              6 |     14 |       4 |             1       |
|         27 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      20 |       0.078  |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |      16 |       0.0614 |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.035  |              4 |    nan |     nan |           nan       |
|         27 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      30 |       0.1183 |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      18 |       0.0617 |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      20 |       0.0784 |             10 |     14 |       4 |             1       |
|         28 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.0373 |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |       8 |       0.0367 |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.0242 |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0169 |              3 |    nan |     nan |           nan       |
|         28 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      10 |       0.05   |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      10 |       0.1075 |              6 |      9 |       3 |             1       |
|         28 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       8 |       0.0622 |              5 |      9 |       3 |             1       |
|         29 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      41 |       0.1317 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      47 |       0.1676 |             18 |     19 |       9 |             1       |
|         29 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      11 |       0.0412 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      87 |       0.2958 |              7 |    nan |     nan |           nan       |
|         29 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     176 |       0.6283 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      54 |       0.1678 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      47 |       0.1851 |             18 |     19 |       9 |             1       |
