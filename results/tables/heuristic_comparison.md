_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

|   reserve | planner                    |   cost | optimal   |   nodes_expanded |   max_frontier | reopenings   | pruned   |   runtime_s | peak_mem_mb            |
|----------:|:---------------------------|-------:|:----------|-----------------:|---------------:|:-------------|:---------|------------:|:-----------------------|
|         0 | UCS                        |    329 | yes       |          1775457 |          41946 | -            | -        |       11.65 | not measured (--quick) |
|         0 | A* + h_manhattan           |    329 | yes       |          1596654 |          47953 | 0            | -        |       14.21 | not measured (--quick) |
|         0 | A* + h_farthest            |    329 | yes       |           686321 |          52912 | 0            | -        |        6.13 | not measured (--quick) |
|         0 | A* + h_mst                 |    329 | yes       |            29542 |          13500 | 4525         | -        |        0.25 | not measured (--quick) |
|         0 | A* + h_ours                |    329 | yes       |            29542 |          13500 | 4525         | -        |        0.3  | not measured (--quick) |
|         0 | Greedy + h_ours            |    485 | no        |            20617 |           7506 | -            | -        |        0.12 | not measured (--quick) |
|         0 | A* + h_ours + fuel pruning |    329 | yes       |             2752 |            852 | 105          | 3878     |        0.07 | not measured (--quick) |
|        20 | UCS                        |    353 | yes       |          1326200 |          30970 | -            | -        |        8.29 | not measured (--quick) |
|        20 | A* + h_manhattan           |    353 | yes       |          1194228 |          34734 | 0            | -        |       10.44 | not measured (--quick) |
|        20 | A* + h_farthest            |    353 | yes       |           596735 |          37340 | 0            | -        |        5.27 | not measured (--quick) |
|        20 | A* + h_mst                 |    353 | yes       |            79615 |          17926 | 11456        | -        |        0.7  | not measured (--quick) |
|        20 | A* + h_ours                |    353 | yes       |            79615 |          17926 | 11456        | -        |        0.69 | not measured (--quick) |
|        20 | Greedy + h_ours            |    541 | no        |            17719 |           5948 | -            | -        |        0.11 | not measured (--quick) |
|        20 | A* + h_ours + fuel pruning |    353 | yes       |             7007 |           1156 | 166          | 9318     |        0.15 | not measured (--quick) |
