_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

|   reserve | planner                    |   cost | optimal   |   nodes_expanded |   max_frontier | reopenings   | pruned   |   runtime_s | peak_mem_mb            |
|----------:|:---------------------------|-------:|:----------|-----------------:|---------------:|:-------------|:---------|------------:|:-----------------------|
|         0 | UCS                        |    329 | yes       |          1775457 |          41946 | -            | -        |       20.39 | not measured (--quick) |
|         0 | A* + h_manhattan           |    329 | yes       |          1596654 |          47953 | 0            | -        |       24.94 | not measured (--quick) |
|         0 | A* + h_farthest            |    329 | yes       |           686321 |          52912 | 0            | -        |       11.38 | not measured (--quick) |
|         0 | A* + h_mst                 |    329 | yes       |            29542 |          13500 | 4525         | -        |        0.44 | not measured (--quick) |
|         0 | A* + h_ours                |    329 | yes       |            29542 |          13500 | 4525         | -        |        0.44 | not measured (--quick) |
|         0 | Greedy + h_ours            |    485 | no        |            20617 |           7506 | -            | -        |        0.2  | not measured (--quick) |
|         0 | A* + h_ours + fuel pruning |    329 | yes       |             2752 |            852 | 105          | 3878     |        0.11 | not measured (--quick) |
|        20 | UCS                        |    353 | yes       |          1326200 |          30970 | -            | -        |       14.21 | not measured (--quick) |
|        20 | A* + h_manhattan           |    353 | yes       |          1194228 |          34734 | 0            | -        |       17.73 | not measured (--quick) |
|        20 | A* + h_farthest            |    353 | yes       |           596735 |          37340 | 0            | -        |        9    | not measured (--quick) |
|        20 | A* + h_mst                 |    353 | yes       |            79615 |          17926 | 11456        | -        |        1.15 | not measured (--quick) |
|        20 | A* + h_ours                |    353 | yes       |            79615 |          17926 | 11456        | -        |        1.11 | not measured (--quick) |
|        20 | Greedy + h_ours            |    541 | no        |            17719 |           5948 | -            | -        |        0.17 | not measured (--quick) |
|        20 | A* + h_ours + fuel pruning |    353 | yes       |             7007 |           1156 | 166          | 9318     |        0.23 | not measured (--quick) |
