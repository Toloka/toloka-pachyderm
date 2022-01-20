pachctl create repo toloka_training_config
pachctl put file toloka_training_config@master:training.json -f ./configs/training.json
pachctl list file toloka_training_config@master
pachctl create pipeline -f toloka_create_training.json
sleep 15s
pachctl list job -p toloka_create_training

pachctl create repo toloka_training_tasks
pachctl put file toloka_training_tasks@master:training_tasks.csv -f ./data/training_tasks.csv
pachctl create pipeline -f toloka_create_training_tasks.json
sleep 15s
pachctl list job -p toloka_create_training_tasks
