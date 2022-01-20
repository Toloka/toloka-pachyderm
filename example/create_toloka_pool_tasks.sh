pachctl create pipeline -f toloka_create_control_tasks.json
sleep 15s
pachctl list job -p toloka_create_control_tasks

pachctl create pipeline -f toloka_create_pool_tasks.json
sleep 15s
pachctl list job -p toloka_create_pool_tasks
