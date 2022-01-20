pachctl create repo toloka_project_config
pachctl put file toloka_project_config@master:project.json -f ./configs/project.json
pachctl list file toloka_project_config@master
pachctl create pipeline -f toloka_create_project.json
sleep 15s
pachctl list job -p toloka_create_project
