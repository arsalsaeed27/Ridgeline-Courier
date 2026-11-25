_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

| variant                      | heuristic         |   h_at_start |   cost | optimal   |   nodes_expanded |   reopenings |   admissibility_violations |   states_checked |
|:-----------------------------|:------------------|-------------:|-------:|:----------|-----------------:|-------------:|---------------------------:|-----------------:|
| h_ours (full)                | h_ours            |          277 |    329 | yes       |            29542 |         4525 |                          0 |              553 |
| - tunnel edges in the fields | h_ours_no_tunnels |          380 |    329 | yes       |            19925 |         5232 |                         17 |              553 |
| - hill costs in the fields   | h_ours_no_hills   |          259 |    329 | yes       |            73121 |         8928 |                          0 |              553 |
| - MST term (= h_farthest)    | h_farthest        |          113 |    329 | yes       |           686321 |            0 |                          0 |              553 |
| - farthest term (= h_mst)    | h_mst             |          277 |    329 | yes       |            29542 |         4525 |                          0 |              553 |
