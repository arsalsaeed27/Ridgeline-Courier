_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

|   instance |   stops |   d_star | algorithm      | solved   | valid_plan   | reason   | goal_test     |   nodes |   runtime_ms |   max_frontier |   cost |   steps |   cost_over_optimal |
|-----------:|--------:|---------:|:---------------|:---------|:-------------|:---------|:--------------|--------:|-------------:|---------------:|-------:|--------:|--------------------:|
|          0 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      10 |       0.0463 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      10 |       0.0533 |              6 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |       6 |       0.0411 |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.0397 |              4 |    nan |     nan |           nan       |
|          0 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      20 |       0.101  |              5 |     10 |       4 |             1       |
|          0 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      14 |       0.062  |              9 |     10 |       4 |             1       |
|          0 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      10 |       0.0584 |              6 |     10 |       4 |             1       |
|          1 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      17 |       0.0667 |             12 |     21 |       5 |             1       |
|          1 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      46 |       0.1657 |             17 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.0241 |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      22 |       0.0789 |              5 |    nan |     nan |           nan       |
|          1 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      41 |       0.1497 |              6 |     21 |       5 |             1       |
|          1 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.1028 |             14 |     21 |       5 |             1       |
|          1 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      46 |       0.1812 |             17 |     21 |       5 |             1       |
|          2 |       3 |        9 | bfs            | True     | True         | solved   | on generation |      88 |       0.2952 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | ucs            | True     | True         | solved   | on pop        |      95 |       0.3813 |             29 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*)        | True     | True         | solved   | on visit      |     177 |       0.5823 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | dls(d*-1)      | False    |              | cutoff   | on visit      |     341 |       1.1669 |              9 |    nan |     nan |           nan       |
|          2 |       3 |        9 | ids            | True     | True         | solved   | on visit      |     904 |       3.7184 |             10 |     27 |       9 |             1       |
|          2 |       3 |        9 | greedy(h_zero) | True     | True         | solved   | on pop        |     108 |       0.4062 |             22 |     27 |       9 |             1       |
|          2 |       3 |        9 | astar(h_zero)  | True     | True         | solved   | on pop        |      95 |       0.4408 |             29 |     27 |       9 |             1       |
|          3 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     152 |       0.5063 |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       0.5907 |             31 |     55 |      15 |             1       |
|          3 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |     245 |       0.9357 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3779 |      14.7471 |             13 |    nan |     nan |           nan       |
|          3 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    9370 |      39.3861 |             14 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.5688 |             29 |     59 |      13 |             1.07273 |
|          3 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       0.6113 |             31 |     55 |      15 |             1       |
|          4 |       3 |       19 | bfs            | True     | True         | solved   | on generation |     165 |       0.5543 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | ucs            | True     | True         | solved   | on pop        |     158 |       0.8183 |             22 |     65 |      21 |             1       |
|          4 |       3 |       19 | dls(d*)        | True     | True         | solved   | on visit      |    2914 |      15.3284 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | dls(d*-1)      | False    |              | cutoff   | on visit      |   81913 |     338.693  |             19 |    nan |     nan |           nan       |
|          4 |       3 |       19 | ids            | True     | True         | solved   | on visit      |  203267 |     903.385  |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | greedy(h_zero) | True     | True         | solved   | on pop        |     170 |       0.5495 |             20 |     77 |      19 |             1.18462 |
|          4 |       3 |       19 | astar(h_zero)  | True     | True         | solved   | on pop        |     158 |       0.5759 |             22 |     65 |      21 |             1       |
|          5 |       2 |       12 | bfs            | True     | True         | solved   | on generation |      72 |       0.2436 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | ucs            | True     | True         | solved   | on pop        |      65 |       0.2322 |             12 |     34 |      12 |             1       |
|          5 |       2 |       12 | dls(d*)        | True     | True         | solved   | on visit      |     874 |       3.1921 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1242 |       4.2656 |             12 |    nan |     nan |           nan       |
|          5 |       2 |       12 | ids            | True     | True         | solved   | on visit      |    3770 |      15.3923 |             13 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |      78 |       0.2644 |             12 |     46 |      12 |             1.35294 |
|          5 |       2 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |      65 |       0.235  |             12 |     34 |      12 |             1       |
|          6 |       2 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.0337 |              7 |      7 |       3 |             1       |
|          6 |       2 |        3 | ucs            | True     | True         | solved   | on pop        |       4 |       0.0227 |              6 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       4 |       0.2139 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0358 |              3 |    nan |     nan |           nan       |
|          6 |       2 |        3 | ids            | True     | True         | solved   | on visit      |       9 |       0.0504 |              4 |      7 |       3 |             1       |
|          6 |       2 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      13 |       0.0504 |             10 |      7 |       3 |             1       |
|          6 |       2 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       4 |       0.0356 |              6 |      7 |       3 |             1       |
|          7 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      26 |       0.1556 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1915 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      27 |       0.1758 |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.2575 |              6 |    nan |     nan |           nan       |
|          7 |       1 |        6 | ids            | True     | True         | solved   | on visit      |     102 |       0.6886 |              7 |     26 |       6 |             1       |
|          7 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.1613 |             10 |     26 |       6 |             1       |
|          7 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1801 |             10 |     26 |       6 |             1       |
|          8 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     207 |       0.6245 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     203 |       0.6691 |             20 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62156 |     256.377  |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |  116025 |     488.172  |             21 |    nan |     nan |           nan       |
|          8 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  385935 |    1685.17   |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     214 |       0.7957 |             22 |     59 |      21 |             1       |
|          8 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     203 |       0.8068 |             20 |     59 |      21 |             1       |
|          9 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.0568 |              5 |     11 |       3 |             1       |
|          9 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.066  |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.044  |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0207 |              3 |    nan |     nan |           nan       |
|          9 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.0719 |              4 |     11 |       3 |             1       |
|          9 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.0483 |              6 |     11 |       3 |             1       |
|          9 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.0559 |              6 |     11 |       3 |             1       |
|         10 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      22 |       0.0873 |             13 |     15 |       5 |             1       |
|         10 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1323 |             18 |     15 |       7 |             1       |
|         10 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      32 |       0.128  |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.082  |              5 |    nan |     nan |           nan       |
|         10 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      66 |       0.2804 |              6 |     15 |       5 |             1       |
|         10 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      36 |       0.135  |             15 |     15 |       5 |             1       |
|         10 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.1369 |             18 |     15 |       7 |             1       |
|         11 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      75 |       0.2472 |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      74 |       0.2849 |             14 |     46 |      14 |             1       |
|         11 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |     994 |       4.1204 |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2000 |       9.1723 |             14 |    nan |     nan |           nan       |
|         11 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    6903 |      32.2851 |             15 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      77 |       0.8603 |             11 |     50 |      14 |             1.08696 |
|         11 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      74 |       0.9907 |             14 |     46 |      14 |             1       |
|         12 |       1 |        6 | bfs            | True     | True         | solved   | on generation |      23 |       0.0962 |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | ucs            | True     | True         | solved   | on pop        |      28 |       0.1065 |             10 |     20 |       6 |             1       |
|         12 |       1 |        6 | dls(d*)        | True     | True         | solved   | on visit      |       7 |       0.0299 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.1524 |              6 |    nan |     nan |           nan       |
|         12 |       1 |        6 | ids            | True     | True         | solved   | on visit      |      82 |       0.3212 |              7 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      29 |       0.0962 |             10 |     26 |       6 |             1.3     |
|         12 |       1 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      28 |       0.1085 |             10 |     20 |       6 |             1       |
|         13 |       3 |       20 | bfs            | True     | True         | solved   | on generation |     150 |       0.7984 |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | ucs            | True     | True         | solved   | on pop        |     168 |       0.8128 |             14 |     76 |      20 |             1       |
|         13 |       3 |       20 | dls(d*)        | True     | True         | solved   | on visit      |     192 |       1.2706 |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | dls(d*-1)      | False    |              | cutoff   | on visit      |    7062 |      26.4773 |             20 |    nan |     nan |           nan       |
|         13 |       3 |       20 | ids            | True     | True         | solved   | on visit      |   27044 |     111.507  |             21 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | greedy(h_zero) | True     | True         | solved   | on pop        |     165 |       0.611  |             17 |     80 |      20 |             1.05263 |
|         13 |       3 |       20 | astar(h_zero)  | True     | True         | solved   | on pop        |     168 |       0.8743 |             14 |     76 |      20 |             1       |
|         14 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      47 |       0.2214 |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      56 |       0.2948 |             16 |     25 |       9 |             1       |
|         14 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      75 |       0.3536 |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      91 |       0.3657 |              7 |    nan |     nan |           nan       |
|         14 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     246 |       0.9227 |              8 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      57 |       0.218  |             16 |     29 |       7 |             1.16    |
|         14 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      56 |       0.2405 |             16 |     25 |       9 |             1       |
|         15 |       3 |       14 | bfs            | True     | True         | solved   | on generation |     128 |       0.5549 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | ucs            | True     | True         | solved   | on pop        |     166 |       1.5434 |             19 |     62 |      18 |             1       |
|         15 |       3 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    6896 |      28.1614 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5429 |      23.6773 |             14 |    nan |     nan |           nan       |
|         15 |       3 |       14 | ids            | True     | True         | solved   | on visit      |   20114 |     186.693  |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |     137 |       0.8908 |             15 |     62 |      14 |             1       |
|         15 |       3 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |     166 |       1.117  |             19 |     62 |      18 |             1       |
|         16 |       3 |       12 | bfs            | True     | True         | solved   | on generation |     131 |       0.7269 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | ucs            | True     | True         | solved   | on pop        |     106 |       0.7395 |             26 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*)        | True     | True         | solved   | on visit      |      72 |       0.52   |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | dls(d*-1)      | False    |              | cutoff   | on visit      |    1916 |      12.0583 |             12 |    nan |     nan |           nan       |
|         16 |       3 |       12 | ids            | True     | True         | solved   | on visit      |    4385 |      20.1894 |             13 |     28 |      12 |             1       |
|         16 |       3 |       12 | greedy(h_zero) | True     | True         | solved   | on pop        |     154 |       0.5728 |             24 |     28 |      12 |             1       |
|         16 |       3 |       12 | astar(h_zero)  | True     | True         | solved   | on pop        |     106 |       0.4339 |             26 |     28 |      12 |             1       |
|         17 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      77 |       0.2944 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      76 |       0.2456 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    2543 |      10.0763 |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3690 |      18.5764 |             14 |    nan |     nan |           nan       |
|         17 |       2 |       14 | ids            | True     | True         | solved   | on visit      |   11158 |      52.806  |             15 |     52 |      14 |             1       |
|         17 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      80 |       0.2431 |             12 |     52 |      14 |             1       |
|         17 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      76 |       0.2314 |             12 |     52 |      14 |             1       |
|         18 |       2 |       14 | bfs            | True     | True         | solved   | on generation |      80 |       0.2522 |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | ucs            | True     | True         | solved   | on pop        |      73 |       0.3595 |             12 |     38 |      14 |             1       |
|         18 |       2 |       14 | dls(d*)        | True     | True         | solved   | on visit      |    1881 |       6.9654 |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | dls(d*-1)      | False    |              | cutoff   | on visit      |    2696 |      13.0016 |             14 |    nan |     nan |           nan       |
|         18 |       2 |       14 | ids            | True     | True         | solved   | on visit      |    8564 |      37.8484 |             15 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | greedy(h_zero) | True     | True         | solved   | on pop        |      86 |       0.7454 |             10 |     52 |      14 |             1.36842 |
|         18 |       2 |       14 | astar(h_zero)  | True     | True         | solved   | on pop        |      73 |       0.3609 |             12 |     38 |      14 |             1       |
|         19 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       7 |       0.0385 |              5 |     11 |       3 |             1       |
|         19 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |      12 |       0.0521 |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       8 |       0.0396 |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0193 |              3 |    nan |     nan |           nan       |
|         19 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      13 |       0.0669 |              4 |     11 |       3 |             1       |
|         19 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      11 |       0.0427 |              6 |     11 |       3 |             1       |
|         19 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |      12 |       0.051  |              6 |     11 |       3 |             1       |
|         20 |       3 |       15 | bfs            | True     | True         | solved   | on generation |     156 |       0.5295 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | ucs            | True     | True         | solved   | on pop        |     145 |       0.7195 |             24 |     51 |      15 |             1       |
|         20 |       3 |       15 | dls(d*)        | True     | True         | solved   | on visit      |    2618 |       8.5059 |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | dls(d*-1)      | False    |              | cutoff   | on visit      |    5655 |      22.966  |             15 |    nan |     nan |           nan       |
|         20 |       3 |       15 | ids            | True     | True         | solved   | on visit      |   18547 |      88.1317 |             16 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | greedy(h_zero) | True     | True         | solved   | on pop        |     160 |       0.9991 |             19 |     55 |      15 |             1.07843 |
|         20 |       3 |       15 | astar(h_zero)  | True     | True         | solved   | on pop        |     145 |       0.9865 |             24 |     51 |      15 |             1       |
|         21 |       2 |        6 | bfs            | True     | True         | solved   | on generation |      30 |       0.1978 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | ucs            | True     | True         | solved   | on pop        |      31 |       0.2362 |             17 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*)        | True     | True         | solved   | on visit      |      48 |       0.3414 |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | dls(d*-1)      | False    |              | cutoff   | on visit      |      41 |       0.296  |              6 |    nan |     nan |           nan       |
|         21 |       2 |        6 | ids            | True     | True         | solved   | on visit      |     123 |       0.8716 |              7 |     16 |       6 |             1       |
|         21 |       2 |        6 | greedy(h_zero) | True     | True         | solved   | on pop        |      40 |       0.2598 |             14 |     16 |       6 |             1       |
|         21 |       2 |        6 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.245  |             17 |     16 |       6 |             1       |
|         22 |       2 |       18 | bfs            | True     | True         | solved   | on generation |      84 |       0.4665 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | ucs            | True     | True         | solved   | on pop        |      82 |       0.5146 |             10 |     70 |      18 |             1       |
|         22 |       2 |       18 | dls(d*)        | True     | True         | solved   | on visit      |   15015 |      87.3545 |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | dls(d*-1)      | False    |              | cutoff   | on visit      |   20543 |      97.0465 |             18 |    nan |     nan |           nan       |
|         22 |       2 |       18 | ids            | True     | True         | solved   | on visit      |   65877 |     303.047  |             19 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | greedy(h_zero) | True     | True         | solved   | on pop        |      88 |       0.5015 |             10 |     72 |      18 |             1.02857 |
|         22 |       2 |       18 | astar(h_zero)  | True     | True         | solved   | on pop        |      82 |       0.4861 |             10 |     70 |      18 |             1       |
|         23 |       2 |        5 | bfs            | True     | True         | solved   | on generation |      19 |       0.0931 |             12 |     17 |       5 |             1       |
|         23 |       2 |        5 | ucs            | True     | True         | solved   | on pop        |      31 |       0.1515 |             14 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*)        | True     | True         | solved   | on visit      |      28 |       0.125  |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | dls(d*-1)      | False    |              | cutoff   | on visit      |      20 |       0.0902 |              5 |    nan |     nan |           nan       |
|         23 |       2 |        5 | ids            | True     | True         | solved   | on visit      |      62 |       0.2842 |              6 |     17 |       5 |             1       |
|         23 |       2 |        5 | greedy(h_zero) | True     | True         | solved   | on pop        |      30 |       0.1224 |             13 |     17 |       5 |             1       |
|         23 |       2 |        5 | astar(h_zero)  | True     | True         | solved   | on pop        |      31 |       0.146  |             14 |     17 |       5 |             1       |
|         24 |       3 |       13 | bfs            | True     | True         | solved   | on generation |     131 |       0.4406 |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | ucs            | True     | True         | solved   | on pop        |     154 |       0.6022 |             23 |     42 |      14 |             1       |
|         24 |       3 |       13 | dls(d*)        | True     | True         | solved   | on visit      |    1795 |       6.6805 |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | dls(d*-1)      | False    |              | cutoff   | on visit      |    3040 |      15.2564 |             13 |    nan |     nan |           nan       |
|         24 |       3 |       13 | ids            | True     | True         | solved   | on visit      |    8542 |      38.4462 |             14 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | greedy(h_zero) | True     | True         | solved   | on pop        |     147 |       0.5427 |             21 |     45 |      13 |             1.07143 |
|         24 |       3 |       13 | astar(h_zero)  | True     | True         | solved   | on pop        |     154 |       0.7198 |             23 |     42 |      14 |             1       |
|         25 |       1 |        2 | bfs            | True     | True         | solved   | on generation |       3 |       0.0226 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | ucs            | True     | True         | solved   | on pop        |       5 |       0.0264 |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*)        | True     | True         | solved   | on visit      |       3 |       0.0163 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | dls(d*-1)      | False    |              | cutoff   | on visit      |       1 |       0.0077 |              2 |    nan |     nan |           nan       |
|         25 |       1 |        2 | ids            | True     | True         | solved   | on visit      |       4 |       0.0256 |              3 |      8 |       2 |             1       |
|         25 |       1 |        2 | greedy(h_zero) | True     | True         | solved   | on pop        |       5 |       0.0201 |              5 |      8 |       2 |             1       |
|         25 |       1 |        2 | astar(h_zero)  | True     | True         | solved   | on pop        |       5 |       0.0221 |              5 |      8 |       2 |             1       |
|         26 |       3 |       21 | bfs            | True     | True         | solved   | on generation |     134 |       0.3609 |             17 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | ucs            | True     | True         | solved   | on pop        |     113 |       0.3749 |             10 |     75 |      21 |             1       |
|         26 |       3 |       21 | dls(d*)        | True     | True         | solved   | on visit      |   62771 |     254.329  |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | dls(d*-1)      | False    |              | cutoff   | on visit      |   79474 |     302.669  |             21 |    nan |     nan |           nan       |
|         26 |       3 |       21 | ids            | True     | True         | solved   | on visit      |  299836 |    1200.91   |             22 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | greedy(h_zero) | True     | True         | solved   | on pop        |     150 |       0.4787 |             18 |     85 |      21 |             1.13333 |
|         26 |       3 |       21 | astar(h_zero)  | True     | True         | solved   | on pop        |     113 |       0.3686 |             10 |     75 |      21 |             1       |
|         27 |       1 |        4 | bfs            | True     | True         | solved   | on generation |      12 |       0.0691 |              6 |     14 |       4 |             1       |
|         27 |       1 |        4 | ucs            | True     | True         | solved   | on pop        |      20 |       0.0955 |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*)        | True     | True         | solved   | on visit      |      16 |       0.073  |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | dls(d*-1)      | False    |              | cutoff   | on visit      |       9 |       0.0407 |              4 |    nan |     nan |           nan       |
|         27 |       1 |        4 | ids            | True     | True         | solved   | on visit      |      30 |       0.139  |              5 |     14 |       4 |             1       |
|         27 |       1 |        4 | greedy(h_zero) | True     | True         | solved   | on pop        |      18 |       0.0724 |             10 |     14 |       4 |             1       |
|         27 |       1 |        4 | astar(h_zero)  | True     | True         | solved   | on pop        |      20 |       0.0916 |             10 |     14 |       4 |             1       |
|         28 |       1 |        3 | bfs            | True     | True         | solved   | on generation |       6 |       0.0322 |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | ucs            | True     | True         | solved   | on pop        |       8 |       0.038  |              5 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*)        | True     | True         | solved   | on visit      |       5 |       0.0267 |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | dls(d*-1)      | False    |              | cutoff   | on visit      |       4 |       0.0213 |              3 |    nan |     nan |           nan       |
|         28 |       1 |        3 | ids            | True     | True         | solved   | on visit      |      10 |       0.0673 |              4 |      9 |       3 |             1       |
|         28 |       1 |        3 | greedy(h_zero) | True     | True         | solved   | on pop        |      10 |       0.0432 |              6 |      9 |       3 |             1       |
|         28 |       1 |        3 | astar(h_zero)  | True     | True         | solved   | on pop        |       8 |       0.0392 |              5 |      9 |       3 |             1       |
|         29 |       2 |        7 | bfs            | True     | True         | solved   | on generation |      41 |       0.1445 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | ucs            | True     | True         | solved   | on pop        |      47 |       0.1848 |             18 |     19 |       9 |             1       |
|         29 |       2 |        7 | dls(d*)        | True     | True         | solved   | on visit      |      11 |       0.0456 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | dls(d*-1)      | False    |              | cutoff   | on visit      |      87 |       0.343  |              7 |    nan |     nan |           nan       |
|         29 |       2 |        7 | ids            | True     | True         | solved   | on visit      |     176 |       0.7296 |              8 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | greedy(h_zero) | True     | True         | solved   | on pop        |      54 |       0.1981 |             16 |     23 |       7 |             1.21053 |
|         29 |       2 |        7 | astar(h_zero)  | True     | True         | solved   | on pop        |      47 |       0.1933 |             18 |     19 |       9 |             1       |
