pachctl create repo toloka_pool
pachctl put file toloka_pool@master:pool.json -f ./configs/pool.json
pachctl put file toloka_pool@master:control_tasks.csv -f ./data/control_tasks.csv
pachctl put file toloka_pool@master:pool_tasks.csv -f ./data/pool_tasks.csv
pachctl list file toloka_pool@master
pachctl create pipeline -f toloka_create_pool.json
sleep 15s
pachctl list job -p toloka_create_pool
